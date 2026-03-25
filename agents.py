import json

from agent import Agent
from email_tools import send_email
from weather import get_weather


def process_refund(item_id, reason="NOT SPECIFIED"):
    """Refund an item. Make sure you have an item_id of the form item_... Ask for user confirmation before processing the refund."""
    return f"Refund processed for {item_id}. Reason: {reason}."


def apply_discount():
    """Apply a discount to the user's cart."""
    return "Applied discount of 11%"


def send_weather_report_email(recipient, location, subject="Weather Report"):
    """Send a weather report email for the exact requested location."""
    weather_raw = get_weather(location=location, time="now")

    try:
        weather_data = json.loads(weather_raw)
    except Exception:
        return f"Email failed: Could not parse weather response for {location}."

    if "error" in weather_data:
        return f"Email failed: {weather_data['error']}"

    resolved_location = weather_data.get("location", location)
    temperature_c = weather_data.get("temperature_c", "N/A")
    feels_like_c = weather_data.get("feels_like_c", "N/A")
    condition = weather_data.get("condition", "N/A")
    humidity = weather_data.get("humidity", "N/A")

    body = (
        f"Here is the current weather report for {resolved_location}:\n\n"
        f"- Location: {resolved_location}\n"
        f"- Temperature: {temperature_c}°C\n"
        f"- Feels Like: {feels_like_c}°C\n"
        f"- Condition: {str(condition).title()}\n"
        f"- Humidity: {humidity}%\n\n"
        "Best regards,\n"
        "Weather Assistant"
    )

    return send_email(recipient=recipient, subject=subject, body=body)


weather_agent = Agent(
    name="Weather Agent",
    instructions=(
        "You are a helpful weather assistant. "
        "Never invent or switch locations. Always use the exact location requested by the user. "
        "If the user asks to send weather by email, call send_weather_report_email and pass the same location. "
        "Use get_weather for non-email weather queries. "
        "If location is missing, ask a follow-up question and do not call tools yet."
    ),
    functions=[get_weather, send_email, send_weather_report_email],
)

triage_agent = Agent(
    name="Triage Agent",
    instructions="""Determine which agent is best suited to handle the user's request, and transfer the conversation to that agent.
- For purchases, pricing, discounts and product inquiries -> Sales Agent
- For refunds, returns and complaints -> Refunds Agent
Never handle requests directly - always transfer to the appropriate specialist.""",
)

sales_agent = Agent(
    name="Sales Agent",
    instructions="Be super enthusiastic about selling bees. Keep responses short, energetic, and focused on closing the sale.",
)

refunds_agent = Agent(
    name="Refunds Agent",
    instructions="Help the user with a refund. If the reason is that it was too expensive, offer a discount first. If they insist, process the refund.",
    functions=[process_refund, apply_discount],
)


def transfer_back_to_triage():
    """Transfer control back to triage when topic no longer matches current specialist."""
    return triage_agent


def transfer_to_sales():
    """Transfer the conversation to the Sales Agent."""
    return sales_agent


def transfer_to_refunds():
    """Transfer the conversation to the Refunds Agent."""
    return refunds_agent


triage_agent.functions = [transfer_to_sales, transfer_to_refunds]
sales_agent.functions.append(transfer_back_to_triage)
refunds_agent.functions.append(transfer_back_to_triage)
