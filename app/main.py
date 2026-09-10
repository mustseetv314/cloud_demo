import platform
import socket
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, HTTPException, Request, status
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, engine, get_db, initialize_database
from app.models import Customer


def seed_customers() -> None:
    with SessionLocal() as db:
        if db.scalar(select(Customer.id).limit(1)) is not None:
            return
        db.add_all(
            [
                Customer(name="John Smith", company="Gateway Manufacturing", email="john@example.com"),
                Customer(name="Jane Miller", company="Northstar Financial", email="jane@example.com"),
                Customer(name="Robert Davis", company="Apex Logistics", email="robert@example.com"),
                Customer(name="Sarah Wilson", company="Summit Retail Group", email="sarah@example.com"),
                Customer(name="Michael Brown", company="Riverfront Healthcare", email="michael@example.com"),
            ]
        )
        db.commit()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    seed_customers()
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def customer_list(request: Request, db: Session = Depends(get_db)):
    customers = db.scalars(select(Customer).order_by(Customer.id)).all()
    return templates.TemplateResponse(
        request=request, name="index.html", context={"customers": customers}
    )


@app.get("/customers/new")
def new_customer_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="customer_form.html",
        context={"customer": None, "title": "Add Customer"},
    )


@app.post("/customers/new")
def new_customer(
    name: str = Form(...),
    company: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    db.add(Customer(name=name.strip(), company=company.strip(), email=email.strip()))
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


def find_customer(customer_id: int, db: Session) -> Customer:
    customer = db.get(Customer, customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@app.get("/customers/{customer_id}/edit")
def edit_customer_form(customer_id: int, request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse(
        request=request,
        name="customer_form.html",
        context={"customer": find_customer(customer_id, db), "title": "Edit Customer"},
    )


@app.post("/customers/{customer_id}/edit")
def edit_customer(
    customer_id: int,
    name: str = Form(...),
    company: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    customer = find_customer(customer_id, db)
    customer.name = name.strip()
    customer.company = company.strip()
    customer.email = email.strip()
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.post("/customers/{customer_id}/delete")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = find_customer(customer_id, db)
    db.delete(customer)
    db.commit()
    return RedirectResponse(url="/", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/health")
def health():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "Healthy", "database": "Connected"}
    except SQLAlchemyError:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "Unhealthy", "database": "Disconnected"},
        )


@app.get("/api/info")
def application_info():
    return {
        "application": settings.app_name,
        "framework": "FastAPI",
        "python_version": platform.python_version(),
        "hostname": socket.gethostname(),
        "environment": settings.app_env,
        "database_provider": "Microsoft SQL Server",
    }


@app.get("/api/customers")
def customer_api(db: Session = Depends(get_db)):
    customers = db.scalars(select(Customer).order_by(Customer.id)).all()
    return [
        {
            "id": customer.id,
            "name": customer.name,
            "company": customer.company,
            "email": customer.email,
            "created_date": customer.created_date.isoformat(),
        }
        for customer in customers
    ]
