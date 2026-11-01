# 🛡️ DisputeIQ: AI-Powered PayPal Dispute Triage

DisputeIQ is a full-stack, AI-driven dashboard designed for merchants to automatically triage, analyze, and resolve PayPal disputes. Built for the **PayPal AI Hackathon**.

## 💡 The Problem
For small and medium businesses, managing chargebacks and disputes is a massive time sink. Merchants must manually review transaction data, tracking numbers, and customer messages to decide whether to refund the customer or fight the dispute. 

## 🚀 The Solution
DisputeIQ listens for PayPal `CUSTOMER.DISPUTE.CREATED` webhooks in real-time. When a dispute is filed, DisputeIQ fetches the transaction data, sends it to **Google Gemini AI** for analysis, and provides the merchant with a clear recommendation: **REFUND**, **FIGHT**, or **PARTIAL REFUND**, along with a drafted response and reasoning. The merchant can resolve the issue with one click.

## 🛠️ Tools & Technologies Used
*   **PayPal Developer Platform**: Utilized the PayPal REST API (OAuth2, Disputes API) and PayPal Webhooks to listen for real-time sandbox events.
*   **Google Gemini AI (`gemini-flash-latest`)**: Used for natural language processing, risk assessment, and drafting merchant responses based on raw JSON dispute data.
*   **FastAPI**: Used to build the high-performance backend server to receive webhooks and process API calls.
*   **Streamlit**: Used to build the interactive, merchant-facing dashboard.
*   **ngrok**: Used to create a secure tunnel to expose the local FastAPI server to PayPal's webhook infrastructure.
*   **SQLite**: Used for lightweight, local database storage of dispute history.



## ⚙️ How to Run Locally 

### 1. Prerequisites
*   Python 3.10+ installed.
*   A PayPal Developer Account (Sandbox).
*   A Google Gemini API Key.
*   ngrok installed.

### 2. Installation
Clone this repository and navigate into the folder:
```bash
git clone https://github.com/Raola-max/disputeiq.git
cd disputeiq