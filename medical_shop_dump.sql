--
-- PostgreSQL database dump
--

\restrict N8bTpP5C0tk4LC2pCDMAdRnOsoFRfWEYOfziRIwOdIbJNrTm2TDWbc2UnDJXHaL

-- Dumped from database version 18.0
-- Dumped by pg_dump version 18.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: customer; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer (
    customer_id integer NOT NULL,
    invoice_number integer NOT NULL,
    customer_name character varying(100) NOT NULL,
    address text,
    phone_number character varying(20) NOT NULL,
    type_id integer
);


ALTER TABLE public.customer OWNER TO postgres;

--
-- Name: customer_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.customer ALTER COLUMN customer_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.customer_customer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: customer_type; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customer_type (
    type_id integer NOT NULL,
    type_name character varying(100) NOT NULL
);


ALTER TABLE public.customer_type OWNER TO postgres;

--
-- Name: in_stock; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.in_stock (
    stock_id integer NOT NULL,
    quantity_of_units integer NOT NULL,
    mfg_date date NOT NULL,
    exp_date date NOT NULL,
    shelf_number character varying(20) NOT NULL,
    product_id integer NOT NULL,
    wholesaler_id integer NOT NULL,
    recieved_date date DEFAULT CURRENT_DATE NOT NULL
);


ALTER TABLE public.in_stock OWNER TO postgres;

--
-- Name: in_stock_stock_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.in_stock_stock_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.in_stock_stock_id_seq OWNER TO postgres;

--
-- Name: in_stock_stock_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.in_stock_stock_id_seq OWNED BY public.in_stock.stock_id;


--
-- Name: in_voice; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.in_voice (
    sales_id integer NOT NULL,
    due_date date,
    status_id integer,
    invoice_date date DEFAULT CURRENT_DATE NOT NULL,
    total_amount numeric(10,2) NOT NULL
);


ALTER TABLE public.in_voice OWNER TO postgres;

--
-- Name: notification; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notification (
    notification_id integer NOT NULL,
    message text NOT NULL,
    is_read boolean DEFAULT false,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.notification OWNER TO postgres;

--
-- Name: notification_notification_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notification_notification_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.notification_notification_id_seq OWNER TO postgres;

--
-- Name: notification_notification_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.notification_notification_id_seq OWNED BY public.notification.notification_id;


--
-- Name: payment_mode; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_mode (
    mode_id integer NOT NULL,
    mode_name character varying(20)
);


ALTER TABLE public.payment_mode OWNER TO postgres;

--
-- Name: payment_status; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payment_status (
    status_id integer NOT NULL,
    status_name character varying(20)
);


ALTER TABLE public.payment_status OWNER TO postgres;

--
-- Name: product; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product (
    product_id integer NOT NULL,
    product_name character varying(100) NOT NULL,
    description text NOT NULL,
    units_of_measure character varying(50),
    mfg_name character varying(200) NOT NULL,
    base_price numeric(10,2) NOT NULL,
    category_id integer,
    reorder_level integer DEFAULT 10 NOT NULL,
    purchase_rate numeric(10,2),
    gst numeric(5,2),
    profit numeric(10,2) GENERATED ALWAYS AS ((base_price - (purchase_rate * ((1)::numeric + (gst / 100.0))))) STORED
);


ALTER TABLE public.product OWNER TO postgres;

--
-- Name: product_category; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.product_category (
    category_id integer NOT NULL,
    category_name character varying(255) NOT NULL
);


ALTER TABLE public.product_category OWNER TO postgres;

--
-- Name: product_category_category_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_category_category_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_category_category_id_seq OWNER TO postgres;

--
-- Name: product_category_category_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_category_category_id_seq OWNED BY public.product_category.category_id;


--
-- Name: product_product_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.product_product_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.product_product_id_seq OWNER TO postgres;

--
-- Name: product_product_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.product_product_id_seq OWNED BY public.product.product_id;


--
-- Name: sale_item; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sale_item (
    quantity_of_order integer DEFAULT 1 NOT NULL,
    discount numeric(5,2) DEFAULT 0.0,
    sale_id integer NOT NULL,
    product_id integer NOT NULL
);


ALTER TABLE public.sale_item OWNER TO postgres;

--
-- Name: sales; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sales (
    sales_id integer NOT NULL,
    sales_date date NOT NULL,
    mode_id integer NOT NULL,
    customer_id integer NOT NULL,
    doctor_name character varying(255) NOT NULL
);


ALTER TABLE public.sales OWNER TO postgres;

--
-- Name: sales_sales_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

ALTER TABLE public.sales ALTER COLUMN sales_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.sales_sales_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: wholesaler; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.wholesaler (
    wholesaler_id integer NOT NULL,
    wholesaler_name character varying(255) NOT NULL,
    mobile_number character varying(20) CONSTRAINT wholesaler_contact_not_null NOT NULL,
    address character varying(255) NOT NULL,
    tax_id character varying(20) NOT NULL,
    email character varying(255),
    drug_license character varying(255)
);


ALTER TABLE public.wholesaler OWNER TO postgres;

--
-- Name: wholesaler_wholesaler_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.wholesaler_wholesaler_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.wholesaler_wholesaler_id_seq OWNER TO postgres;

--
-- Name: wholesaler_wholesaler_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.wholesaler_wholesaler_id_seq OWNED BY public.wholesaler.wholesaler_id;


--
-- Name: in_stock stock_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_stock ALTER COLUMN stock_id SET DEFAULT nextval('public.in_stock_stock_id_seq'::regclass);


--
-- Name: notification notification_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification ALTER COLUMN notification_id SET DEFAULT nextval('public.notification_notification_id_seq'::regclass);


--
-- Name: product product_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product ALTER COLUMN product_id SET DEFAULT nextval('public.product_product_id_seq'::regclass);


--
-- Name: product_category category_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_category ALTER COLUMN category_id SET DEFAULT nextval('public.product_category_category_id_seq'::regclass);


--
-- Name: wholesaler wholesaler_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wholesaler ALTER COLUMN wholesaler_id SET DEFAULT nextval('public.wholesaler_wholesaler_id_seq'::regclass);


--
-- Data for Name: customer; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer (customer_id, invoice_number, customer_name, address, phone_number, type_id) FROM stdin;
1	1001	Rohan Sharma	101 Palm Heights, Kothrud, Pune	9988776655	1
2	1002	Priya Mehta	202 Sunrise Apts, Koregaon Park, Pune	9988776644	2
3	1003	Amit Patel	303 River View, Andheri, Mumbai	9988776633	1
4	1004	Sneha Rao	404 Green Valley, Baner, Pune	9988776622	1
5	1005	Vikram Singh	505 Royal Towers, Wakad, Pune	9988776611	2
6	1006	Ananya Desai	B-11, Harmony, Aundh, Pune	9988776600	2
7	1007	Rajesh Kumar	707 Prestige Point, Hinjewadi, Pune	9988775599	1
8	1008	Meera Iyer	8/A, Shanti Vihar, PCMC, Pune	9988775588	1
9	1009	Arjun Reddy	Flat 12, Deccan Gymkhana, Pune	9988775577	2
10	1010	Fatima Sheikh	22B, MG Road, Pune	9988775566	2
\.


--
-- Data for Name: customer_type; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.customer_type (type_id, type_name) FROM stdin;
1	Regular
2	Retailer
\.


--
-- Data for Name: in_stock; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.in_stock (stock_id, quantity_of_units, mfg_date, exp_date, shelf_number, product_id, wholesaler_id, recieved_date) FROM stdin;
1	100	2024-01-01	2026-01-01	A-1	11	1	2025-01-15
2	50	2024-06-01	2025-12-01	A-1	11	2	2025-02-10
3	80	2024-03-01	2026-03-01	B-2	12	1	2025-03-05
4	60	2024-05-01	2025-11-01	C-4	13	3	2025-04-20
5	40	2024-08-01	2026-08-01	C-4	13	3	2025-05-15
6	120	2024-04-01	2027-04-01	D-1	14	2	2025-06-11
7	200	2024-02-01	2028-02-01	E-3	15	1	2025-07-22
8	70	2024-10-01	2026-10-01	B-2	12	1	2025-08-01
9	30	2024-11-01	2025-11-01	D-1	14	2	2025-09-30
10	50	2024-09-01	2026-09-01	A-1	11	1	2025-10-05
\.


--
-- Data for Name: in_voice; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.in_voice (sales_id, due_date, status_id, invoice_date, total_amount) FROM stdin;
2	\N	1	2025-10-26	100.00
3	2025-11-10	2	2025-10-27	299.25
4	2025-11-15	2	2025-10-28	115.50
5	\N	1	2025-10-28	530.00
6	\N	1	2025-10-28	84.00
7	2025-11-28	2	2025-10-28	85.00
8	\N	1	2025-10-29	490.00
9	2025-11-15	2	2025-10-29	169.00
10	\N	1	2025-10-29	289.50
\.


--
-- Data for Name: notification; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.notification (notification_id, message, is_read, created_at) FROM stdin;
1	Alert: Bill #4 for customer Amit Patel is due tomorrow.	f	2025-11-14 08:00:00
2	NEAR EXPIRY: 50 units of Paracetamol (Stock ID 2) are expiring on 2025-12-01.	f	2025-11-01 08:00:00
3	LOW STOCK: Vitamin C 500mg has only 70 units left. Reorder level is 30.	f	2025-10-28 09:15:00
4	SLOW MOVING: 200 units of Sterile Gauze (Stock ID 7) have been in stock since 2025-07-22.	f	2025-12-25 08:00:00
\.


--
-- Data for Name: payment_mode; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_mode (mode_id, mode_name) FROM stdin;
1	Cash
2	UPI
3	Card
4	Insurance
5	Credit
\.


--
-- Data for Name: payment_status; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.payment_status (status_id, status_name) FROM stdin;
1	Paid
2	Balance
\.


--
-- Data for Name: product; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product (product_id, product_name, description, units_of_measure, mfg_name, base_price, category_id, reorder_level, purchase_rate, gst) FROM stdin;
11	Paracetamol 500mg	Strip of 10 tablets for fever and pain.	Strip of 10	Cipla	30.50	1	10	20.00	5.00
12	Amoxicillin 250mg	Strip of 12 capsules, antibiotic.	Strip of 12	Sun Pharma	85.00	2	10	60.00	12.00
13	Antacid Gel	200ml bottle for acidity and gas.	200ml Bottle	GSK	110.00	3	10	75.00	12.00
14	Vitamin C 500mg	Bottle of 30 chewable tablets.	Bottle of 30	Abbott	99.75	4	10	65.00	5.00
15	Sterile Gauze	Box of 5 large sterile gauze pads.	Box of 5	Johnson & Johnson	75.20	5	10	50.00	5.00
16	Baby Diapers (M)	Pack of 30 medium size diapers.	Pack of 30	Pampers	450.00	5	10	350.00	5.00
17	Antiseptic Soap	125g bar of antiseptic soap.	125g Bar	Dettol	45.00	4	10	30.00	18.00
18	Digital Thermometer	Waterproof digital thermometer.	1 Unit	Omron	250.00	3	10	180.00	18.00
19	Crepe Bandage (4in)	4-inch roll of cotton crepe bandage.	1 Roll	Hansaplast	120.00	2	10	80.00	5.00
20	Amlodipine 5mg	Strip of 10 for blood pressure.	Strip of 10	Zydus	42.00	1	10	25.00	12.00
\.


--
-- Data for Name: product_category; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.product_category (category_id, category_name) FROM stdin;
1	Painkillers & Fever
2	Antibiotics
3	Antacids & Digestive
4	Cough, Cold & Flu
5	Vitamins & Supplements
\.


--
-- Data for Name: sale_item; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sale_item (quantity_of_order, discount, sale_id, product_id) FROM stdin;
1	10.00	2	11
3	0.00	3	14
1	0.00	4	11
1	0.00	4	12
1	0.00	5	16
2	10.00	5	17
2	0.00	6	11
1	0.00	7	20
\.


--
-- Data for Name: sales; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.sales (sales_id, sales_date, mode_id, customer_id, doctor_name) FROM stdin;
2	2025-10-25	1	1	Dr. Gupta
3	2025-10-26	3	2	Dr. Sen
4	2025-10-27	2	1	Dr. Gupta
5	2025-10-28	1	3	Dr. Joshi
6	2025-10-28	1	5	Dr. Sen
7	2025-10-28	2	6	Dr. Iyer
8	2025-10-28	3	7	Dr. Gupta
9	2025-10-29	1	8	Dr. Sen
10	2025-10-29	2	9	Dr. Bose
11	2025-10-29	3	10	Dr. Sen
\.


--
-- Data for Name: wholesaler; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.wholesaler (wholesaler_id, wholesaler_name, mobile_number, address, tax_id, email, drug_license) FROM stdin;
1	Pharma Distributors	9876543210	123 Warehouse Rd, Mumbai	GSTIN123ABC	contact@pharmadist.com	MH/123/XYZ
2	HealthCo Supplies	9876543211	456 Market St, Pune	GSTIN456DEF	sales@healthco.in	MH/456/PQR
3	QuickMed Ltd.	9876543212	789 Logistics Park, Delhi	GSTIN789GHI	info@quickmed.co.in	DL/789/LMN
4	Apex Medical	9123456780	B-12, MIDC, Nagpur	GSTIN987ZYX	accounts@apexmed.com	MH/987/UVW
5	Surya Pharma	9123456781	77 Kothrud Ind. Area, Pune	GSTIN987WVT	purchase@suryapharma.net	MH/654/RST
6	Medicare Inc.	9123456782	5B, Malad, Mumbai	GSTIN987USR	support@medicareinc.org	MH/321/KLN
7	National Medico	9123456783	G-9, Connaught Place, Delhi	GSTIN987TQP	orders@nationalmedico.com	DL/012/OPQ
8	Deccan Drugs	9123456784	Plot 4, Begumpet, Hyderabad	GSTIN987ONM	info@deccandrugs.in	TS/345/DEF
9	Wellness For All	9123456785	C-1, Salt Lake, Kolkata	GSTIN987LKI	contact@wellnessforall.co	WB/678/ABC
10	Jeevan Rakshak	9123456786	22A, T. Nagar, Chennai	GSTIN987JHG	sales@jeevanrakshak.com	TN/901/GHI
\.


--
-- Name: customer_customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customer_customer_id_seq', 10, true);


--
-- Name: in_stock_stock_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.in_stock_stock_id_seq', 10, true);


--
-- Name: notification_notification_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.notification_notification_id_seq', 4, true);


--
-- Name: product_category_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_category_category_id_seq', 5, true);


--
-- Name: product_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.product_product_id_seq', 20, true);


--
-- Name: sales_sales_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.sales_sales_id_seq', 11, true);


--
-- Name: wholesaler_wholesaler_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.wholesaler_wholesaler_id_seq', 10, true);


--
-- Name: customer customer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_pkey PRIMARY KEY (customer_id);


--
-- Name: customer_type customer_type_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_type
    ADD CONSTRAINT customer_type_pkey PRIMARY KEY (type_id);


--
-- Name: customer_type customer_type_type_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer_type
    ADD CONSTRAINT customer_type_type_name_key UNIQUE (type_name);


--
-- Name: in_stock in_stock_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_stock
    ADD CONSTRAINT in_stock_pkey PRIMARY KEY (stock_id);


--
-- Name: in_voice in_voice_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_voice
    ADD CONSTRAINT in_voice_pkey PRIMARY KEY (sales_id);


--
-- Name: notification notification_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.notification
    ADD CONSTRAINT notification_pkey PRIMARY KEY (notification_id);


--
-- Name: payment_mode payment_mode_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_mode
    ADD CONSTRAINT payment_mode_pkey PRIMARY KEY (mode_id);


--
-- Name: payment_status payment_status_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payment_status
    ADD CONSTRAINT payment_status_pkey PRIMARY KEY (status_id);


--
-- Name: product_category product_category_category_name_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_category
    ADD CONSTRAINT product_category_category_name_key UNIQUE (category_name);


--
-- Name: product_category product_category_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product_category
    ADD CONSTRAINT product_category_pkey PRIMARY KEY (category_id);


--
-- Name: product product_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_pkey PRIMARY KEY (product_id);


--
-- Name: sale_item sale_item_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_item
    ADD CONSTRAINT sale_item_pkey PRIMARY KEY (sale_id, product_id);


--
-- Name: sales sales_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_pkey PRIMARY KEY (sales_id);


--
-- Name: wholesaler unique_drug_license; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wholesaler
    ADD CONSTRAINT unique_drug_license UNIQUE (drug_license);


--
-- Name: wholesaler wholesaler_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wholesaler
    ADD CONSTRAINT wholesaler_pkey PRIMARY KEY (wholesaler_id);


--
-- Name: wholesaler wholesaler_tax_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.wholesaler
    ADD CONSTRAINT wholesaler_tax_id_key UNIQUE (tax_id);


--
-- Name: customer customer_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customer
    ADD CONSTRAINT customer_type_id_fkey FOREIGN KEY (type_id) REFERENCES public.customer_type(type_id);


--
-- Name: in_stock in_stock_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_stock
    ADD CONSTRAINT in_stock_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(product_id);


--
-- Name: in_stock in_stock_wholesaler_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_stock
    ADD CONSTRAINT in_stock_wholesaler_id_fkey FOREIGN KEY (wholesaler_id) REFERENCES public.wholesaler(wholesaler_id);


--
-- Name: in_voice in_voice_sales_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_voice
    ADD CONSTRAINT in_voice_sales_id_fkey FOREIGN KEY (sales_id) REFERENCES public.sales(sales_id);


--
-- Name: in_voice in_voice_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.in_voice
    ADD CONSTRAINT in_voice_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.payment_status(status_id);


--
-- Name: product product_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.product
    ADD CONSTRAINT product_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.product_category(category_id);


--
-- Name: sale_item sale_item_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_item
    ADD CONSTRAINT sale_item_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.product(product_id);


--
-- Name: sale_item sale_item_sale_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sale_item
    ADD CONSTRAINT sale_item_sale_id_fkey FOREIGN KEY (sale_id) REFERENCES public.sales(sales_id);


--
-- Name: sales sales_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customer(customer_id);


--
-- Name: sales sales_mode_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.sales
    ADD CONSTRAINT sales_mode_id_fkey FOREIGN KEY (mode_id) REFERENCES public.payment_mode(mode_id);


--
-- PostgreSQL database dump complete
--

\unrestrict N8bTpP5C0tk4LC2pCDMAdRnOsoFRfWEYOfziRIwOdIbJNrTm2TDWbc2UnDJXHaL

