# PayPal Sandbox Integration Guide

FINORA integrates with the official PayPal REST APIs (v2) for checkout and order capture.

## 1. Prerequisites
1. A PayPal Developer Account: [https://developer.paypal.com](https://developer.paypal.com)
2. A Sandbox App with REST API credentials (Client ID and Client Secret).

## 2. Environment Configuration
Add your credentials to `.env` or `backend/.env`:

```env
PAYPAL_MODE=sandbox
PAYPAL_CLIENT_ID=your_paypal_sandbox_client_id_here
PAYPAL_CLIENT_SECRET=your_paypal_sandbox_client_secret_here
PAYPAL_API_BASE=https://api-m.sandbox.paypal.com
```

> **Note:** If no credentials are provided, FINORA automatically runs in **Integrated Sandbox Simulation Mode**. In this mode, genuine PayPal Sandbox JSON payloads and order IDs are generated so all hackathon review workflows can be demonstrated offline with zero friction.

## 3. Checkout Workflow

1. **Product Selection & Landed Cost Calculation**:
   - The user selects a product in the Shopping Agent.
   - The backend computes the landed cost: `total_cost = item_price + shipping_cost`.
2. **Order Creation (`POST /api/payments/create-order`)**:
   - The backend authenticates with PayPal OAuth 2.0 (`/v1/oauth2/token`).
   - The order is created via `/v2/checkout/orders` with intent `CAPTURE`.
3. **User Approval**:
   - The user reviews the payment breakdown and approves the checkout.
4. **Order Capture (`POST /api/payments/capture-order`)**:
   - The server calls `/v2/checkout/orders/{order_id}/capture`.
   - The capture is verified, stored in the permanent payments ledger, and duplicate captures are blocked.
