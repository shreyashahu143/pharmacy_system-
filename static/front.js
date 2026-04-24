/**
 * URL of the Flask backend.
 * Now served from the same origin, so an empty string '' works.
 */
const API_BASE_URL = '';

/**
 * Parses a string value to a float, returning 0 if invalid.
 * @param {string} value - The string to parse.
 * @returns {number} The parsed float or 0.
 */
function safeParseFloat(value) {
    const num = parseFloat(value);
    return isNaN(num) ? 0 : num;
}

/**
 * Clears all product-related fields.
 */
function clearProductFields() {
    document.getElementById('productNameInput').value = '';
    document.getElementById('productMrpRef').value = '0.00';
    document.getElementById('productBatchRef').value = '';
    document.getElementById('productShelfRef').value = '';
    document.getElementById('productExpiryRef').value = '';
}

/**
 * Fetches product details from the backend API when a Product ID is entered.
 */
async function fetchProductDetails() {
    const productId = document.getElementById('productIdInput').value.trim().toUpperCase();
    
    if (!productId) {
        clearProductFields();
        calculateTotal();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}/api/product/${productId}`);
        
        if (response.ok) {
            // Product found
            const product = await response.json();
            document.getElementById('productNameInput').value = product.name;
            document.getElementById('productMrpRef').value = product.mrp.toFixed(2);
            document.getElementById('productBatchRef').value = product.batch;
            document.getElementById('productShelfRef').value = product.shelf;
            document.getElementById('productExpiryRef').value = product.expiry;
        } else {
            // Product not found (404) or other error
            clearProductFields();
            document.getElementById('productNameInput').value = 'Product Not Found';
        }
    } catch (error) {
        // Network error or server is down
        console.error('Error fetching product:', error);
        clearProductFields();
        document.getElementById('productNameInput').value = 'Error connecting to server';
    }

    // Update the suggested line total
    calculateTotal(); 
}

/**
 * Calculates the total line item amount based on quantity and MRP.
 * This function also updates the main "TOTAL AMOUNT" field.
 */
function calculateTotal() {
    const totalQuantity = safeParseFloat(document.getElementById('totalQuantity').value);
    const fixedMrp = safeParseFloat(document.getElementById('productMrpRef').value);
    const suggestedLineTotal = fixedMrp * totalQuantity;

    // Update the Line Total (Ref) field
    document.querySelector('.line-total').value = suggestedLineTotal.toFixed(2);
    
    // LOGICAL FIX: Also update the main 'Total Amount' field
    document.getElementById('totalAmountDisplay').value = suggestedLineTotal.toFixed(2);
    
    // Trigger balance calculation
    calculateBalance(); 
}

/**
 * Calculates the final balance due based on Total Amount and Amount Paid.
 */
function calculateBalance() {
    const totalAmount = safeParseFloat(document.getElementById('totalAmountDisplay').value); 
    const amountPaid = safeParseFloat(document.getElementById('amountPaid').value);
    const balance = totalAmount - amountPaid;
    
    document.getElementById('balanceDisplay').value = balance.toFixed(2);
    
    // Set due date if there is a balance
    const dueDateInput = document.getElementById('dueDate');
    if (balance > 0.01) { 
        const today = new Date();
        today.setDate(today.getDate() + 7); // Default 7 days due
        dueDateInput.valueAsDate = today;
    } else {
        dueDateInput.value = '';
    }
}

/**
 * Gathers all form data and POSTs it to the backend API to save the sale.
 */
async function handleSubmit() {
    // 1. Gather all data from the form into an object
    const saleData = {
        billNumber: document.getElementById('billNumber').value,
        saleDate: document.getElementById('saleDate').value,
        patientName: document.getElementById('patientName').value,
        customerType: document.getElementById('customerType1').value,
        totalQuantity: document.getElementById('totalQuantity').value,
        paymentMode: document.getElementById('paymentMode1').value,
        
        totalAmount: document.getElementById('totalAmountDisplay').value,
        amountPaid: document.getElementById('amountPaid').value,
        balanceAmount: document.getElementById('balanceDisplay').value,
        dueDate: document.getElementById('dueDate').value,
        
        // Product info
        productId: document.getElementById('productIdInput').value.trim().toUpperCase(),
        productName: document.getElementById('productNameInput').value,
        productMrp: document.getElementById('productMrpRef').value,
        productBatch: document.getElementById('productBatchRef').value,
        productShelf: document.getElementById('productShelfRef').value,
        productExpiry: document.getElementById('productExpiryRef').value,
        lineTotal: document.querySelector('.line-total').value
    };

    // 2. Send the data to the backend
    try {
        const response = await fetch(`${API_BASE_URL}/api/sale`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(saleData)
        });
        
        const result = await response.json();

        if (response.ok) { // HTTP 200-299
            showMessage('Success!', result.message, 'success');
            // Successfully submitted, fetch the next bill number for a new sale
            fetchNextBillNumber();
            // Optionally, you could clear the form here
        } else {
            // Show error message from the server (e.g., 404, 409, 500)
            showMessage('Error', result.description || 'An unknown error occurred.', 'error');
        }
    } catch (error) {
        // Network error
        console.error('Error submitting sale:', error);
        showMessage('Network Error', 'Could not connect to the server. Please try again.', 'error');
    }
}

/**
 * Fetches the next available bill number from the API.
 */
async function fetchNextBillNumber() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/next-bill-number`);
        if (response.ok) {
            const data = await response.json();
            document.getElementById('billNumber').value = data.next_bill_number;
        } else {
            document.getElementById('billNumber').value = 'B-ERR';
        }
    } catch (error) {
        console.error('Error fetching next bill number:', error);
        document.getElementById('billNumber').value = 'B-OFFLINE';
    }
}

/**
 * Shows the custom message box.
 * @param {string} title - The title for the message box.
 * @param {string} text - The main text for the message box.
 * @param {'success'|'error'} type - The type of message.
 */
function showMessage(title, text, type = 'success') {
    const overlay = document.getElementById('messageOverlay');
    const messageBox = document.getElementById('messageBox');
    document.getElementById('messageTitle').textContent = title;
    document.getElementById('messageText').textContent = text;
    
    messageBox.className = type; // 'success' or 'error'
    overlay.style.display = 'flex';
}

/**
 * Closes the custom message box.
 */
function closeMessage() {
    document.getElementById('messageOverlay').style.display = 'none';
}


// --- ON PAGE LOAD ---

/**
 * Runs when the page is first loaded.
 * Sets the default sale date and fetches the starting bill number.
 */
document.addEventListener('DOMContentLoaded', () => {
    // Set sale date to today
    document.getElementById('saleDate').valueAsDate = new Date();
    
    // Fetch the next available bill number from the backend
    fetchNextBillNumber();
    
    // Initialize calculations
    calculateBalance();
});