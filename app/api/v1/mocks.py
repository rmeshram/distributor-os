import random
from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter(prefix="/mocks", tags=["Mocks"])

# ERP Mocks

# Tally ODBC simulates XML integrations
TALLY_STOCK_XML = """<ENVELOPE>
    <HEADER>
        <VERSION>1</VERSION>
        <STATUS>SUCCESS</STATUS>
    </HEADER>
    <BODY>
        <STOCK_DATA>
            <ROW>
                <SKU>PROD-HUL-SOAP</SKU>
                <ON_HAND>500</ON_HAND>
                <COMMITTED>50</COMMITTED>
            </ROW>
            <ROW>
                <SKU>PROD-ITC-AATA</SKU>
                <ON_HAND>150</ON_HAND>
                <COMMITTED>12</COMMITTED>
            </ROW>
        </STOCK_DATA>
    </BODY>
</ENVELOPE>"""

@router.post("/tally/query", response_class=Response)
def mock_tally_odbc_query(request_xml: str = None):
    """
    Simulates Tally XML-based ODBC query API.
    """
    # Simply return the mocked stock levels XML
    return Response(content=TALLY_STOCK_XML, media_type="application/xml")


@router.get("/marg/inventory")
def mock_marg_inventory():
    """
    Simulates Marg REST API for inventory synchronization.
    """
    return {
        "status": "success",
        "data": [
            {"item_code": "PROD-HUL-SOAP", "qty": 450, "rate": 42.0},
            {"item_code": "PROD-ITC-AATA", "qty": 138, "rate": 250.0}
        ]
    }


@router.get("/busy/stock-status")
def mock_busy_stock_status():
    """
    Simulates Busy stock status query API.
    """
    return {
        "BusyVersion": "21.0",
        "Result": "Success",
        "Items": [
            {"ItemCode": "PROD-HUL-SOAP", "Stock": 450.00, "PendingSales": 50.00},
            {"ItemCode": "PROD-ITC-AATA", "Stock": 138.00, "PendingSales": 12.00}
        ]
    }


# Logistics Mocks

class ShipmentRequest(BaseModel):
    order_id: str
    destination_address: str
    recipient_name: str
    weight_kg: float

@router.post("/delhivery/create-shipment")
def mock_delhivery_create_shipment(payload: ShipmentRequest):
    """
    Simulates Delhivery's shipment booking API.
    """
    tracking_id = f"DELH{random.randint(100000000, 999999999)}"
    return {
        "success": True,
        "waybill": tracking_id,
        "status": "In Transit",
        "destination": payload.destination_address,
        "carrier": "Delhivery"
    }


@router.post("/bluedart/create-waybill")
def mock_bluedart_create_waybill(payload: ShipmentRequest):
    """
    Simulates Blue Dart's waybill generation API.
    """
    waybill_no = f"BD{random.randint(10000000, 99999999)}"
    return {
        "status": "WAYBILL_GENERATED",
        "waybill": waybill_no,
        "details": {
            "shipper": "DistributorOS Warehouse",
            "consignee": payload.recipient_name,
            "destination": payload.destination_address
        },
        "carrier": "Blue Dart"
    }


@router.get("/tracking/{tracking_id}")
def mock_tracking_status(tracking_id: str):
    """
    Simulates standard tracking status lookup.
    """
    if tracking_id.startswith("DELH"):
        return {"tracking_id": tracking_id, "carrier": "Delhivery", "status": "In Transit", "eta": "2 Days"}
    elif tracking_id.startswith("BD"):
        return {"tracking_id": tracking_id, "carrier": "Blue Dart", "status": "Out for Delivery", "eta": "Today"}
    else:
        return {"tracking_id": tracking_id, "carrier": "Unknown", "status": "Shipped", "eta": "Unknown"}
