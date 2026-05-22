import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

class InvoiceService:
    @staticmethod
    def generate_order_invoice_base64(order):
        """
        Generates a PDF invoice for an order and returns it as a base64 string.
        """
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)

        # Header
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1 * inch, 10.5 * inch, f"INVOICE - {order.pharmacy.name}")

        p.setFont("Helvetica", 12)
        p.drawString(1 * inch, 10 * inch, f"Order ID: {order.id}")
        p.drawString(1 * inch, 9.75 * inch, f"Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(1 * inch, 9.5 * inch, f"Customer: {order.user.username}")

        # Table Header
        p.line(1 * inch, 9 * inch, 7.5 * inch, 9 * inch)
        p.drawString(1 * inch, 8.75 * inch, "Item")
        p.drawString(4 * inch, 8.75 * inch, "Qty")
        p.drawString(6 * inch, 8.75 * inch, "Price")
        p.line(1 * inch, 8.6 * inch, 7.5 * inch, 8.6 * inch)

        # Items
        y = 8.35 * inch
        for item in order.items.all():
            p.drawString(1 * inch, y, f"{item.inventory_item.medicine.name}")
            p.drawString(4 * inch, y, f"{item.quantity}")
            p.drawString(6 * inch, y, f"Rs. {item.price_at_order}")
            y -= 0.25 * inch

        # Total
        p.line(1 * inch, y, 7.5 * inch, y)
        y -= 0.3 * inch
        p.setFont("Helvetica-Bold", 12)
        p.drawString(1 * inch, y, f"Total Amount: Rs. {order.total_amount}")

        p.showPage()
        p.save()

        buffer.seek(0)
        pdf_data = buffer.getvalue()
        return base64.b64encode(pdf_data).decode('utf-8')
