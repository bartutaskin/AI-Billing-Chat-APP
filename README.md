# 🌐 MobileProviderAPI Gateway

This project serves as the **API Gateway** for the [MobileProviderAPI](https://github.com/bartutaskin/MobileProviderAPI). Built using **Ocelot**, the gateway routes incoming requests to the appropriate downstream microservices deployed on Azure.

---

## 📦 Overview

The API Gateway abstracts internal service URLs and exposes a unified interface for frontend clients (like the AI Chat App or mobile apps) to interact with:

- Authentication (`/login`, `/register`)
- Billing (`/calculate`, `/pay`)
- Querying bills (detailed and summary)
- Submitting usage

All requests are routed securely over HTTPS to the backend hosted at:
https://mobileproviderbt-egbra3excxgpfndy.italynorth-01.azurewebsites.net

---

## 🚀 Exposed Endpoints

| Method | Gateway Path                                 | Routed To (Backend API)                          |
|--------|-----------------------------------------------|--------------------------------------------------|
| POST   | `/gateway/Auth/login`                         | `/api/v1/Auth/login`                             |
| POST   | `/gateway/Auth/register`                      | `/api/v1/Auth/register`                          |
| POST   | `/gateway/Bill/calculate`                     | `/api/v1/Bill/calculate`                         |
| POST   | `/gateway/Bill/pay`                           | `/api/v1/Bill/pay`                               |
| GET    | `/gateway/QueryBill/query`                    | `/api/v1/QueryBill/query`                        |
| GET    | `/gateway/QueryBillDetailed/query-detailed`   | `/api/v1/QueryBillDetailed/query-detailed`       |
| POST   | `/gateway/Usage/usage`                        | `/api/v1/Usage/usage`                            |

---

## 🧠 Design & Architecture

- **Gateway Pattern**: Implements the API Gateway pattern using [Ocelot](https://ocelot.readthedocs.io/en/latest/), commonly used in .NET microservices.
- **Centralized Routing**: All upstream requests starting with `/gateway/*` are routed to the appropriate microservice endpoint.
- **HTTPS Support**: Both upstream and downstream traffic is routed securely over HTTPS.

---

## 🛠️ Setup & Configuration

1. **Clone the Repository**

```bash
git clone https://github.com/your-username/MobileProviderGateway.git
cd MobileProviderGateway
```

2. **Install Dependencies**

```bash
dotnet restore
```

3. **Ocelot Configuration**

```bash
"UpstreamPathTemplate": "/gateway/Bill/pay",
"DownstreamPathTemplate": "/api/v1/Bill/pay",
"DownstreamHostAndPorts": [
  { "Host": "mobileproviderbt-egbra3excxgpfndy.italynorth-01.azurewebsites.net", "Port": 443 }
]
```

4. **Run Locally**

```bash
dotnet run
```

## 🔗 Related Repositories

- [MobileProviderAPI](https://github.com/bartutaskin/MobileProviderAPI) – Main backend services
- [Chat UI App](https://github.com/bartutaskin/SE4458-AI-CHAT-APP) – React-based AI chat assistant (optional integration)
- [AI Agent](https://github.com/bartutaskin/SE4458-AI-AGENT) AI agent backend that processes user queries and interacts with billing APIs.

