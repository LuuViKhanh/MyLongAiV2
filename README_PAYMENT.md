# Hướng dẫn tích hợp thanh toán — MyLongAI

Base URL: `https://mylongaiv2.onrender.com`

---

## Tổng quan

Hệ thống thanh toán dùng **chuyển khoản ngân hàng** kết hợp **SePay webhook** để tự động nâng cấp tài khoản lên Premium.

```
User bấm "Nâng cấp Premium"
        ↓
POST /payment/create-order  →  nhận mã đơn + QR
        ↓
Hiển thị QR cho user quét và chuyển khoản
        ↓
SePay nhận tiền → tự động gọi webhook
        ↓
Server nâng cấp role = "premium"
        ↓
Frontend poll GET /auth/profile → role = "premium" → thông báo thành công
```

---

## API

### POST `/payment/create-order` 🔒

Tạo đơn hàng mới. Gọi khi user bấm **"Nâng cấp Premium"**.

**Header:**
```
Authorization: Bearer <access_token>
```

**Response thành công:**
```json
{
  "order_code": "MLAI123456",
  "amount": 10000,
  "bank_account": "96247812005",
  "bank_name": "BIDV",
  "account_name": "LUU VI KHANH",
  "content": "MLAI123456",
  "qr_url": "https://img.vietqr.io/image/BIDV-96247812005-compact2.png?amount=10000&addInfo=MLAI123456&accountName=LUU%20VI%20KHANH"
}
```

**Lỗi:**
| Code | Mô tả |
|------|-------|
| 400 | Tài khoản đã là Premium |
| 401 | Chưa đăng nhập |

> Mỗi lần gọi sẽ **hủy đơn pending cũ** và tạo đơn mới — không cần lo đơn tồn đọng.

---

### GET `/payment/status` 🔒

Kiểm tra trạng thái đơn hàng mới nhất.

**Response:**
```json
{
  "id": "uuid",
  "order_code": "MLAI123456",
  "amount": 10000,
  "status": "pending",
  "created_at": "2025-01-01T10:00:00",
  "paid_at": null
}
```

| `status` | Ý nghĩa |
|----------|---------|
| `pending` | Chờ thanh toán |
| `paid` | Đã thanh toán thành công |
| `cancelled` | Đã hủy (tạo đơn mới) |

---

## Hiển thị trang thanh toán

### Bước 1 — Tạo đơn hàng

```js
const BASE_URL = 'https://mylongaiv2.onrender.com'

async function createOrder() {
  const res = await fetch(`${BASE_URL}/payment/create-order`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}` }
  })

  if (res.status === 400) {
    alert('Tài khoản đã là Premium!')
    return
  }

  const order = await res.json()
  showPaymentPage(order)
}
```

### Bước 2 — Hiển thị QR

```html
<!-- Hiển thị QR VietQR — tự điền sẵn STK + số tiền + nội dung -->
<img src="{{ order.qr_url }}" alt="QR thanh toán" width="300" />

<!-- Hoặc hiển thị thông tin thủ công -->
<p>Ngân hàng: {{ order.bank_name }}</p>
<p>Số tài khoản: {{ order.bank_account }}</p>
<p>Tên: {{ order.account_name }}</p>
<p>Số tiền: {{ order.amount | currency }}</p>
<p>Nội dung: <strong>{{ order.content }}</strong></p>
```

> ⚠️ **Quan trọng:** User phải ghi đúng nội dung `MLAI123456` khi chuyển khoản thủ công. Nếu quét QR thì nội dung tự điền sẵn.

---

### Bước 3 — Tự động kiểm tra đã thanh toán chưa

Sau khi hiển thị QR, poll `/auth/profile` mỗi 5 giây:

```js
function startPolling() {
  const interval = setInterval(async () => {
    const profile = await fetch(`${BASE_URL}/auth/profile`, {
      headers: { 'Authorization': `Bearer ${token}` }
    }).then(r => r.json())

    if (profile.role === 'premium') {
      clearInterval(interval)
      // Cập nhật lại token/profile trong app
      showSuccessMessage()
      redirectToDashboard()
    }
  }, 5000) // kiểm tra mỗi 5 giây

  // Dừng sau 15 phút nếu không thanh toán
  setTimeout(() => clearInterval(interval), 15 * 60 * 1000)
}
```

---

## Phân biệt Free vs Premium

Sau khi đăng nhập, kiểm tra `role` từ `GET /auth/profile`:

```js
const profile = await fetch(`${BASE_URL}/auth/profile`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json())

if (profile.role === 'premium') {
  // Hiện đầy đủ tính năng
} else {
  // Ẩn tính năng premium, hiện nút "Nâng cấp"
}
```

| Tính năng | Free | Premium |
|-----------|------|---------|
| Xem nhiệt độ, độ ẩm realtime | ✅ | ✅ |
| Lịch sử cảm biến | ✅ 2 ngày | ✅ Không giới hạn |
| AI detect bánh | ✅ 10 lần/ngày | ✅ Không giới hạn |
| Khuyến nghị thời tiết | ❌ | ✅ |
| AI dự đoán thời gian phơi | ❌ | ✅ |
| Số camera | ✅ 1 camera | ✅ Không giới hạn |

---

## Xử lý lỗi 403

Khi Free user gọi API Premium, server trả về:

```json
{
  "detail": "Cần nâng cấp Premium để sử dụng tính năng này"
}
```

Frontend xử lý:

```js
if (res.status === 403) {
  showUpgradeModal() // Hiện popup "Nâng cấp Premium"
}
```

---

## Flow đầy đủ (React example)

```jsx
function UpgradePage() {
  const [order, setOrder] = useState(null)
  const [isPaid, setIsPaid] = useState(false)

  const handleUpgrade = async () => {
    const res = await fetch(`${BASE_URL}/payment/create-order`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}` }
    })
    const data = await res.json()
    setOrder(data)
    startPolling()
  }

  const startPolling = () => {
    const interval = setInterval(async () => {
      const profile = await fetch(`${BASE_URL}/auth/profile`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }).then(r => r.json())

      if (profile.role === 'premium') {
        clearInterval(interval)
        setIsPaid(true)
      }
    }, 5000)
    setTimeout(() => clearInterval(interval), 15 * 60 * 1000)
  }

  if (isPaid) return <div>🎉 Nâng cấp thành công!</div>

  if (!order) return <button onClick={handleUpgrade}>Nâng cấp Premium</button>

  return (
    <div>
      <img src={order.qr_url} alt="QR thanh toán" width={300} />
      <p>Số tiền: {order.amount.toLocaleString()}đ</p>
      <p>Nội dung: <strong>{order.content}</strong></p>
      <p>⏳ Đang chờ thanh toán...</p>
    </div>
  )
}
```

---

## Lưu ý quan trọng

- QR VietQR **tự điền sẵn** STK + số tiền + nội dung khi quét bằng app ngân hàng
- Thời gian nâng cấp sau khi chuyển khoản: **5-30 giây**
- Nếu quá 15 phút chưa nâng cấp → tạo đơn mới và thử lại
- Không cần user nhập gì thêm, chỉ cần quét QR và xác nhận
