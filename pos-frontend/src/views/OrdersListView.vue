<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo.jpg" alt="Pub Express" />
      </div>
      <nav class="sidebar-nav">
        <ul>
          <router-link
            v-for="item in menuNavItems"
            :key="item.path"
            :to="item.path"
            custom
            v-slot="{ navigate, href, isActive }"
          >
            <li :class="{ active: isActive }" @click="navigate" :href="href">
              {{ item.name }}
            </li>
          </router-link>
        </ul>
      </nav>
      <div class="sidebar-version">
        <small>v{{ appVersion }}</small>
      </div>
    </aside>

    <div class="content-wrapper">
      <header class="topbar">Orders History</header>

      <div class="page-content">
        <div class="top-controls">
          <input
            v-model="searchQuery"
            class="search-input"
            placeholder="Search by order # or item name..."
          />
          <div class="date-filters">
            <input type="date" v-model="startDate" />
            <span>to</span>
            <input type="date" v-model="endDate" />
          </div>
        </div>

        <!-- Status Filters -->
        <div class="filter-categories">
          <button
            @click="filterStatus = 'paid'"
            :class="{ active: filterStatus === 'paid' }"
          >
            Paid
          </button>
          <button
            @click="filterStatus = 'void'"
            :class="{ active: filterStatus === 'void' }"
          >
            Void
          </button>
          <button
            @click="filterStatus = 'all'"
            :class="{ active: filterStatus === 'all' }"
          >
            All
          </button>
          <button
            @click="filterStatus = 'held'"
            :class="{ active: filterStatus === 'held' }"
          >
            Held
          </button>
        </div>

        <div v-if="loading">Loading orders...</div>
        <div v-else-if="error" class="error">{{ error }}</div>

        <div v-else class="dashboard-cards">
          <div
            v-for="order in filteredOrders"
            :key="order.id"
            class="dashboard-card"
            :class="{
              'card-green': order.is_paid,
              'card-red': order.cancel_reason,
              'card-yellow':
                !order.is_paid &&
                !order.cancel_reason &&
                order.status === 'held',
            }"
          >
            <h3>Order #{{ order.id }}</h3>
            <p>
              <strong>₱{{ order.total.toFixed(2) }}</strong> — {{ order.type }}
            </p>
            <p>Date: {{ new Date(order.created_at).toLocaleString() }}</p>
            <p>
              Status:
              <span v-if="order.cancel_reason" class="badge cancel">Void</span>
              <span v-else-if="order.is_paid" class="badge paid">Paid</span>
              <span v-else-if="order.status === 'held'" class="badge held"
                >Held</span
              >
            </p>

            <div class="menu-buttons">
              <button @click="reviewOrder(order.id)">Review</button>
              <button class="cancel-btn" @click="deleteOrder(order.id)">
                Delete
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "../axios";

const appVersion = __APP_VERSION__;

export default {
  data() {
    return {
      orders: [],
      loading: true,
      error: "",
      filterStatus: "paid",
      searchQuery: "",
      startDate: "",
      endDate: "",
      appVersion: __APP_VERSION__,
    };
  },
  computed: {
    filteredOrders() {
      return this.orders
        .filter((order) => {
          if (this.filterStatus === "paid")
            return order.is_paid && !order.cancel_reason;
          if (this.filterStatus === "void") return !!order.cancel_reason;
          if (this.filterStatus === "held") return order.status === "held";
          return true; // all
        })
        .filter((order) => {
          const query = this.searchQuery.toLowerCase();
          return (
            order.id.toString().includes(query) ||
            order.items.some((item) =>
              item.menu_item.name.toLowerCase().includes(query)
            )
          );
        })
        .filter((order) => {
          if (!this.startDate && !this.endDate) return true;

          const orderDateObj = new Date(order.created_at);
          const orderDate = orderDateObj.toLocaleDateString("en-CA");

          const from = this.startDate || "0000-01-01";
          const to = this.endDate || "9999-12-31";

          return orderDate >= from && orderDate <= to;
        });
    },
    menuNavItems() {
      return [
        { name: "Cashier", path: "/cashier-modern" },
        { name: "Daily Sales", path: "/dashboard" },
        { name: "Reports", path: "/summary" },
        { name: "Menu", path: "/menu" },
        { name: "Orders", path: "/orders-list" },
        { name: "Supervisor Tools", path: "/supervisor-tools" },
      ];
    },
  },
  async mounted() {
    await this.fetchOrders();
  },
  methods: {
    async fetchOrders() {
      try {
        const res = await api.get("http://localhost:8000/orders");
        this.orders = res.data;
      } catch (err) {
        this.error = "Failed to fetch orders.";
      } finally {
        this.loading = false;
      }
    },
    reviewOrder(orderId) {
      this.$router.push({
        name: "ReceiptView",
        params: { orderId },
        query: { from: "orders" },
      });
    },
    async deleteOrder(orderId) {
      const confirmDelete = confirm(
        `Delete Order #${orderId}? This cannot be undone.`
      );
      if (!confirmDelete) return;

      try {
        await api.delete(`http://localhost:8000/orders/${orderId}`);
        alert(`Order #${orderId} deleted.`);
        await this.fetchOrders();
      } catch (err) {
        alert("Failed to delete order.");
      }
    },
  },
};
</script>

<style scoped>
@import "../assets/dashboardview.css";

.search-input {
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid #ccc;
  font-size: 15px;
  flex: 1;
  min-width: 250px;
}

.date-filters input {
  padding: 6px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.filter-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.filter-categories button {
  background-color: #cecece;
  color: #222;
  border-radius: 20px;
  padding: 6px 12px;
  border: none;
  cursor: pointer;
}

.filter-categories button.active {
  background-color: #f7c948;
  color: black;
}

/* ===== ORDER CARDS COLORS ===== */
.dashboard-card {
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #222; /* Always readable */
}

.dashboard-card.card-green {
  background-color: #63d37b; /* Paid */
}

.dashboard-card.card-gray {
  background-color: #ffbcbc; /* Canceled/Void */
}

.dashboard-card.card-yellow {
  background-color: #ffe078; /* Held or unpaid */
}

.dashboard-card h3 {
  margin: 0;
  font-size: 18px;
}

.dashboard-card p {
  margin: 2px 0;
  font-size: 15px;
}

/* ===== BADGES ===== */
.badge {
  border-radius: 10px;
  padding: 2px 8px;
  font-size: 13px;
}

.badge.paid {
  background-color: #28a745;
  color: white;
}

.badge.cancel {
  background-color: #b82325;
  color: white;
}

.badge.held {
  background-color: #ffc107;
  color: #333;
}

/* ===== BUTTONS ===== */
.menu-buttons button {
  background-color: #333;
  color: white;
  border: none;
  padding: 5px 10px;
  margin: 4px;
  border-radius: 4px;
}

.menu-buttons button:hover {
  background-color: #555;
}

.cancel-btn {
  background-color: #dc3545;
  color: white;
}

.top-controls {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 10px;
  align-items: center;
}

.card-red {
  background-color: #7e7272;
  color: #fff;
}

.sidebar-version {
  margin-top: auto;
  padding: 10px;
  font-size: 13px;
  text-align: center;
  color: #ccc;
}
</style>
