"""
Invoices Service
project_code: invoices-s01
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uuid
import datetime

app = FastAPI(title="Invoices Service")

# In-memory база данных
invoices_db = []


class InvoiceCreate(BaseModel):
    amount: float
    description: str
    customer_name: str


class Invoice(InvoiceCreate):
    id: str
    status: str
    created_at: str
    updated_at: str


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "invoices-svc-s01"}


@app.get("/api/invoices", response_model=List[Invoice])
async def get_invoices():
    return invoices_db


@app.get("/api/invoices/{invoice_id}", response_model=Invoice)
async def get_invoice(invoice_id: str):
    for invoice in invoices_db:
        if invoice["id"] == invoice_id:
            return invoice
    raise HTTPException(status_code=404, detail="Invoice not found")


@app.post("/api/invoices", response_model=Invoice, status_code=201)
async def create_invoice(invoice: InvoiceCreate):
    now = datetime.datetime.now().isoformat()
    new_invoice = Invoice(
        id=str(uuid.uuid4())[:8],
        amount=invoice.amount,
        description=invoice.description,
        customer_name=invoice.customer_name,
        status="PENDING",
        created_at=now,
        updated_at=now
    )
    invoices_db.append(new_invoice.dict())
    return new_invoice


@app.delete("/api/invoices/{invoice_id}")
async def delete_invoice(invoice_id: str):
    for i, invoice in enumerate(invoices_db):
        if invoice["id"] == invoice_id:
            invoices_db.pop(i)
            return {"message": "Invoice deleted"}
    raise HTTPException(status_code=404, detail="Invoice not found")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8268)