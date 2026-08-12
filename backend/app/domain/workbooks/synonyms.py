"""Global Trade Synonym Dictionary for intelligent header matching."""

from collections.abc import Sequence


class GlobalSynonymDictionary:
    """Hierarchical synonym dictionary for trade terminology.

    Hierarchy: Template Alias → Industry Dictionary → Global Trade Dictionary
    """

    def __init__(self) -> None:
        self._entries: dict[str, list[str]] = {}
        self._load_global_entries()

    def _load_global_entries(self) -> None:
        self._entries = {
            # ── Consignee ──────────────────────────────────────
            "consignee": [
                "Consignee",
                "Consignee Name",
                "Consignee Address",
                "Consignee & Consignee_Address",
                "Consignee and Consignee Address",
                "Consignee & Address",
                "Importer",
                "Importer Name",
                "Importer Address",
                "Buyer",
                "Buyer Name",
                "Notify Party",
                "Customer",
                "Customer Name",
                "Receiver",
                "Consignee/Notify",
            ],
            # ── Port / Destination Port ────────────────────────
            "port": [
                "Port",
                "Port Name",
                "Port of Discharge",
                "Discharge Port",
                "Destination Port",
                "Loading Port",
                "Port of Loading",
                "POL",
                "Port of Arrival",
                "POD",
                "PORT_CD",
                "Port Code",
                "Unloading Port",
            ],
            # ── Indian Port / Origin Port ──────────────────────
            "indian_port": [
                "Indian Port",
                "Port of Loading",
                "Loading Port",
                "POL",
                "Departure Port",
                "Origin Port",
                "Export Port",
                "Loading Point",
            ],
            # ── CUSH (Port Code) ────────────────────────────────
            "cush": [
                "CUSH",
                "CUSH Code",
                "Port Code Loading",
                "Loading Port Code",
                "Origin Port Code",
                "Port Code",
                "Indian Port Code",
            ],
            # ── Date ────────────────────────────────────────────
            "date": [
                "Date",
                "Shipment Date",
                "Export Date",
                "Transaction Date",
                "Invoice Date",
                "Document Date",
                "Loading Date",
                "Discharge Date",
            ],
            # ── IEC (Importer Exporter Code) ─────────────────────
            "iec": [
                "IEC",
                "IEC Code",
                "Importer Exporter Code",
                "IE Code",
                "Import Export Code",
                "Exporter IEC",
                "PAN",
                "GSTIN",
            ],
            # ── Exporter / Shipper ───────────────────────────────
            "exporter": [
                "Exporter",
                "Exporter Name",
                "Exporter_Name",
                "Shipper",
                "Supplier",
                "Seller",
                "Vendor",
                "Manufacturer",
                "Exporting Company",
            ],
            # ── Exporter Address ─────────────────────────────────
            "exporter_address": [
                "Exporter Address",
                "Exporter_Address",
                "Shipper Address",
                "Supplier Address",
                "Registered Address",
                "Business Address",
            ],
            # ── Exporter City / State ────────────────────────────
            "exporter_city_state": [
                "Exporter City State",
                "Exporter_City_State",
                "Exporter City",
                "Shipper City",
                "Origin City",
                "Exporter Location",
                "City State",
            ],
            # ── Exporter PIN ─────────────────────────────────────
            "exporter_pin": [
                "Exporter PIN",
                "Exporter_PIN",
                "Exporter Pincode",
                "Shipper PIN",
                "Shipper Zip",
                "Postal Code",
                "Pincode",
                "PIN Code",
            ],
            # ── Country ─────────────────────────────────────────
            "country": [
                "Country",
                "COUNTRY",
                "Country of Origin",
                "Origin Country",
                "Destination Country",
                "Import Country",
                "Receiving Country",
                "Export Country",
                "Country of Export",
                "Consignee Country",
                "Country Name",
            ],
            # ── HS Code ─────────────────────────────────────────
            "hs_code": [
                "HS",
                "HS Code",
                "HSN",
                "HSN Code",
                "Commodity Code",
                "Tariff Code",
                "Tariff Heading",
                "Harmonized System",
                "Product Code",
                "ITC HS Code",
                "RITC",
                "ITC Code",
            ],
            # ── CHP ─────────────────────────────────────────────
            "chp": [
                "CHP",
                "CHP Code",
                "CHP Rate",
                "Custom House Code",
                "Customs Code",
            ],
            # ── Description ─────────────────────────────────────
            "description": [
                "Description",
                "Product Description",
                "Goods Description",
                "Item Description",
                "Commodity Description",
                "Cargo Description",
                "Product Details",
                "Item Details",
            ],
            # ── Quantity / Weight ────────────────────────────────
            "quantity": [
                "Quantity",
                "Qty",
                "Quantity (MT)",
                "Net Weight",
                "Gross Weight",
                "Weight",
                "Volume",
                "Pieces",
                "Units",
                "Packages",
                "Pkgs",
                "Net Qty",
            ],
            # ── UQC / Unit of Measure ────────────────────────────
            "uqc": [
                "UQC",
                "Unit",
                "Unit of Quantity",
                "Unit Code",
                "UOM",
                "Unit of Measure",
                "Measurement Unit",
                "Quantity Unit",
                "Packing Unit",
            ],
            # ── Unit Price / Rate ────────────────────────────────
            "unit_price": [
                "Unit Price",
                "Rate",
                "Price per Unit",
                "Unit Rate",
                "Price/Unit",
                "Unit Rate in FC",
                "Rate per Unit",
                "Unit Value",
                "FC Rate",
            ],
            # ── Currency ─────────────────────────────────────────
            "currency": [
                "Currency",
                "FC Currency",
                "Invoice Currency",
                "Transaction Currency",
                "Foreign Currency",
                "Currency Code",
                "FC",
            ],
            # ── FOB Value / Price ────────────────────────────────
            "fob_value": [
                "FOB",
                "FOB Value",
                "FOB Price",
                "FOB Amount",
                "Invoice Value",
                "Invoice Amount",
                "Total Amount",
                "Total Value",
                "Amount (USD)",
                "Declared Value",
                "Shipment Value",
                "Free on Board",
            ],
            # ── Invoice Number ───────────────────────────────────
            "invoice_number": [
                "Invoice",
                "Invoice Number",
                "Invoice No",
                "Inv No",
                "Bill of Lading",
                "B/L",
                "BL Number",
                "Container Number",
                "Container No",
            ],
            # ── Container ────────────────────────────────────────
            "container": [
                "Container",
                "Container Number",
                "Container No",
                "Container ID",
                "Container Size",
                "Seal Number",
                "Seal No",
            ],
            # ── Shipping Company / Carrier ───────────────────────
            "shipping_company": [
                "Shipping Line",
                "Carrier",
                "Vessel Operator",
                "Shipping Company",
                "Transporter",
                "Vessel",
                "Shipping Agent",
                "Forwarder",
            ],
        }

    def get(self, business_field: str) -> list[str]:
        return self._entries.get(business_field.lower(), [])

    @property
    def all_business_fields(self) -> tuple[str, ...]:
        return tuple(self._entries.keys())


class IndustrySynonymDictionary:
    """Industry-specific synonyms layered on top of global dictionary."""

    def __init__(self, global_dict: GlobalSynonymDictionary) -> None:
        self._global = global_dict
        self._industry_entries: dict[str, list[str]] = {}

    def add_industry_synonyms(self, field: str, synonyms: Sequence[str]) -> None:
        key = field.lower()
        self._industry_entries.setdefault(key, [])
        for s in synonyms:
            if s not in self._industry_entries[key]:
                self._industry_entries[key].append(s)

    def get_all(self, business_field: str) -> list[str]:
        key = business_field.lower()
        industry = self._industry_entries.get(key, [])
        global_entries = self._global.get(business_field)
        seen = set()
        merged: list[str] = []
        for alias in industry + global_entries:
            lower = alias.lower()
            if lower not in seen:
                seen.add(lower)
                merged.append(alias)
        return merged


# ── Trade Terminology Patterns ─────────────────────────────────


COMMON_COUNTRY_NAMES: tuple[str, ...] = (
    "India",
    "Indonesia",
    "Thailand",
    "Vietnam",
    "Pakistan",
    "Myanmar",
    "Cambodia",
    "Bangladesh",
    "Nepal",
    "Sri Lanka",
    "China",
    "Japan",
    "South Korea",
    "Taiwan",
    "Singapore",
    "Malaysia",
    "Philippines",
    "Brazil",
    "Argentina",
    "Uruguay",
    "Paraguay",
    "USA",
    "United States",
    "Canada",
    "Mexico",
    "United Kingdom",
    "Germany",
    "France",
    "Italy",
    "Spain",
    "Netherlands",
    "Belgium",
    "Poland",
    "Russia",
    "Turkey",
    "UAE",
    "Saudi Arabia",
    "Iran",
    "Iraq",
    "Yemen",
    "South Africa",
    "Nigeria",
    "Kenya",
    "Egypt",
    "Morocco",
    "Australia",
    "New Zealand",
)

COMMON_PORT_NAMES: tuple[str, ...] = (
    "Rotterdam",
    "Hamburg",
    "Antwerp",
    "Singapore",
    "Shanghai",
    "Hong Kong",
    "Busan",
    "Jebel Ali",
    "Colombo",
    "Nhava Sheva",
    "Mundra",
    "Chennai",
    "Kolkata",
    "Visakhapatnam",
    "Paradip",
    "Kandla",
    "Cochin",
    "Mumbai",
    "Krishnapatnam",
    "Chittagong",
    "Yangon",
    "Ho Chi Minh",
    "Haiphong",
    "Da Nang",
    "Bangkok",
    "Laem Chabang",
    "Jakarta",
    "Surabaya",
    "Manila",
    "Karachi",
    "Los Angeles",
    "Long Beach",
    "New York",
    "Houston",
    "Felixstowe",
    "Southampton",
    "Le Havre",
    "Marseille",
    "Genoa",
    "Trieste",
    "Barcelona",
    "Valencia",
    "Piraeus",
)

COMMON_HS_CODE_PREFIXES: tuple[str, ...] = (
    "10",  # Cereals
    "1006",  # Rice
    "100620",  # Husked rice
    "100630",  # Semi/wholly milled rice
    "100640",  # Broken rice
)

COMMON_CURRENCY_SYMBOLS: tuple[str, ...] = ("$", "€", "£", "¥", "₹")
