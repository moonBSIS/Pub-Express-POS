<template>
  <div>
    <!-- Receipt Buttons (NOT inside print area) -->
    <div class="receipt-buttons">
      <button @click="print">🖨️ Print Receipt</button>
      <button @click="printFailsafePDF">🖨️ Failsafe Print (PDF)</button>
      <button @click="generateLargePDF">📄 Failsafe (Larger PDF)</button>
      <button @click="goBack">🔙 Back to Orders</button>
    </div>

    <!-- Printable Receipt -->
    <div v-if="order" class="receipt" ref="printArea">
      <div class="header">
        <p v-if="order.receipt_number">Receipt #: {{ order.receipt_number }}</p>
        <p v-if="order.cashier">Cashier: {{ order.cashier }}</p>
        <hr />
      </div>

      <div class="items">
        <div v-for="item in order.items" :key="item.id" class="item-row">
          <div class="item-name">{{ item.menu_item.name }}</div>
          <div class="item-details">
            <span>Qty: {{ item.quantity }}</span>
            <span> ₱{{ finalItemPrice(item).toFixed(2) }} </span>
          </div>
          <div v-if="item.notes" class="note">Note: {{ item.notes }}</div>
        </div>
      </div>

      <div v-if="discountMeta" class="discount-meta">
        <p><strong>Customer Name:</strong> {{ discountMeta.name }}</p>
        <p><strong>Discount Type:</strong> {{ discountMeta.type }}</p>
      </div>

      <hr />
      <div class="totals">
        <div>
          <span>Subtotal</span><span>₱{{ subtotal }}</span>
        </div>
        <div>
          <span>Discount</span><span>₱{{ discount }}</span>
        </div>
        <div>
          <span>Total</span><span>₱{{ total }}</span>
        </div>
        <div>
          <span>Paid</span><span>₱{{ paid }}</span>
        </div>
        <div>
          <span>Change</span><span>₱{{ change.toFixed(2) }}</span>
        </div>
      </div>

      <div class="footer">
        <p>Date/Time: {{ formatDate(order.created_at) }}</p>
        <div class="qr-wrapper">
          <img :src="qrUrl" alt="QR Code" class="qr" />
          <p class="thanks">{{ receiptFooter }}</p>
        </div>
        <p class="thanks">THIS IS NOT AN OFFICIAL RECEIPT</p>
      </div>
    </div>

    <div v-else>
      <p>Loading receipt...</p>
    </div>
  </div>
</template>

<script>
import api from "../axios";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

export default {
  data() {
    return {
      order: null,
      qrUrl: "",
      receiptFooter: "",
    };
  },
  computed: {
    subtotal() {
      if (!this.order) return "0.00";

      return this.order.items
        .reduce((sum, item) => {
          let base = item.menu_item.price;

          // Exclude VAT if marked
          if (item.vat_applied) base *= 100 / 112;

          let lineTotal = base * item.quantity;

          // Apply per-item discount
          if (item.manual_discount_type === "fixed") {
            lineTotal -= item.manual_discount_value;
          } else if (item.manual_discount_type === "percent") {
            lineTotal -= (item.manual_discount_value / 100) * lineTotal;
          }

          return sum + lineTotal;
        }, 0)
        .toFixed(2);
    },
    discount() {
      return Number(this.order?.discount || 0).toFixed(2);
    },
    total() {
      return (
        Number(this.order?.total || 0) - Number(this.order?.discount || 0)
      ).toFixed(2);
    },
    paid() {
      return Number(this.order?.paid || 0).toFixed(2);
    },
    change() {
      return this.order
        ? this.order.paid - (this.order.total - this.order.discount)
        : 0;
    },
    discountMeta() {
      if (!this.order) return null;
      const item = this.order.items.find(
        (i) => i.discount_person_name && i.discount_person_type
      );
      return item
        ? { name: item.discount_person_name, type: item.discount_person_type }
        : null;
    },
  },
  async mounted() {
    const orderId = this.$route.params.orderId;
    const qrRes = await api.get("/settings/qr-link");
    const link = qrRes.data.value || "";
    this.qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=${encodeURIComponent(
      link
    )}`;

    try {
      const res = await api.get(`http://localhost:8000/orders/${orderId}`);
      this.order = res.data;

      this.$nextTick(() => {
        setTimeout(() => this.print(), 500);
      });
    } catch (err) {
      console.error("Failed to fetch order for receipt:", err);
    }
    const msgRes = await api.get("/settings/receipt-message");
    this.receiptFooter = msgRes.data.value || "Claim your Sweet Treat!";
  },
  methods: {
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleString();
    },
    print() {
      window.print();
    },
    goBack() {
      this.$router.push("/cashier-modern");
    },
    finalItemPrice(item) {
      let base = item.menu_item.price;
      if (item.vat_applied) base *= 100 / 112;
      let total = base * item.quantity;

      if (item.manual_discount_type === "fixed") {
        total -= item.manual_discount_value;
      } else if (item.manual_discount_type === "percent") {
        total -= (item.manual_discount_value / 100) * total;
      }

      return Math.max(0, total);
    },
    printFailsafePDF() {
      const el = this.$refs.printArea;
      html2canvas(el, { scale: 2 }).then((canvas) => {
        const imgData = canvas.toDataURL("image/png");
        const pdfHeight = (canvas.height * 58) / canvas.width;

        const pdf = new jsPDF({
          orientation: "portrait",
          unit: "mm",
          format: [58, pdfHeight],
        });

        pdf.addImage(imgData, "PNG", 0, 0, 58, pdfHeight);
        window.open(pdf.output("bloburl"), "_blank");
      });
    },
    generateLargePDF() {
      const el = this.$refs.printArea;
      html2canvas(el, { scale: 3 }).then((canvas) => {
        const imgData = canvas.toDataURL("image/png");
        const pdf = new jsPDF({
          orientation: "portrait",
          unit: "mm",
          format: [80, (canvas.height * 80) / canvas.width],
        });
        pdf.addImage(
          imgData,
          "PNG",
          0,
          0,
          80,
          (canvas.height * 80) / canvas.width
        );
        window.open(pdf.output("bloburl"), "_blank");
      });
    },
  },
};
</script>

<style scoped>
.receipt {
  width: 58mm;
  font-family: "Courier New", Courier, monospace;
  font-size: 14px;
  background: white;
  color: #000;
  line-height: 1.6;
  padding-top: 30px;
  margin: auto;
}

.header,
.footer {
  text-align: center;
  margin-bottom: 8px;
}

.items {
  margin-bottom: 8px;
}

.item-row {
  margin-bottom: 4px;
}

.item-name {
  font-weight: bold;
}

.item-details {
  display: flex;
  justify-content: space-between;
}

.note {
  font-size: 12px;
  color: #444;
  margin-left: 5px;
}

.discount-meta {
  border-top: 1px dashed #000;
  margin-top: 10px;
  padding-top: 6px;
}

.totals {
  border-top: 1px dashed #000;
  margin-top: 10px;
  padding-top: 5px;
}

.totals div {
  display: flex;
  justify-content: space-between;
  margin: 2px 0;
}

.qr-wrapper {
  margin-top: 10px;
}

.qr {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  display: block;
}

.thanks {
  font-weight: bold;
  margin-top: 6px;
  font-size: 13px;
  text-align: center;
}

/* Outside of receipt for buttons */
.receipt-buttons {
  text-align: center;
  margin: 12px 0;
}

.receipt-buttons button {
  margin: 4px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
}

@media print {
  .receipt-buttons {
    display: none;
  }
}
</style>
