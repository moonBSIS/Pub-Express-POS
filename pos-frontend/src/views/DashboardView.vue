<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo.jpg" alt="Pub Express" />
      </div>
      <nav class="sidebar-nav">
        <ul>
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            custom
            v-slot="{ navigate, href, isActive }"
          >
            <li
              :class="{ active: isActive }"
              @click="navigate"
              :href="href"
              style="cursor: pointer"
            >
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
      <header class="topbar">Daily Sales</header>
      <div class="page-content">
        <div class="breadcrumb-filter">
          <div class="breadcrumb">Home &gt; Daily Sales</div>
        </div>
        <section class="dashboard-cards">
          <!-- Total Sales -->
          <div class="dashboard-card card-red">
            <div class="card-label">
              ₱{{ todaySummary.total_sales.toFixed(2) }}
            </div>
            <div class="card-caption">Total Sales</div>
          </div>

          <!-- Total Discount -->
          <div class="dashboard-card card-yellow">
            <div class="card-label">
              ₱{{ todaySummary.total_discount.toFixed(2) }}
            </div>
            <div class="card-caption">Total Discounts</div>
          </div>

          <!-- Total Orders -->
          <div class="dashboard-card card-red">
            <div class="card-label">{{ todaySummary.total_orders }}</div>
            <div class="card-caption">Total Orders</div>
          </div>

          <!-- Void Orders -->
          <div class="dashboard-card card-yellow">
            <div class="card-label">
              {{ todaySummary.void_orders }}
            </div>
            <div class="card-caption">Orders Void</div>
          </div>
        </section>
        <section class="dashboard-chart">
          <div class="chart-header">
            SALES CHART ( {{ labels[0] }} - {{ labels[labels.length - 1] }} )
          </div>
          <canvas id="salesChart" />
        </section>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import api from "../axios";

const appVersion = __APP_VERSION__;

const menuItems = [
  { name: "Cashier", path: "/cashier-modern" },
  { name: "Daily Sales", path: "/dashboard" },
  { name: "Reports", path: "/summary" },
  { name: "Menu", path: "/menu" },
  { name: "Orders", path: "/orders-list" },
  { name: "Supervisor Tools", path: "/supervisor-tools" },
];

const labels = ref<string[]>([]);
const salesData = ref<number[]>([]);

const todaySummary = ref({
  total_sales: 0,
  total_discount: 0,
  total_orders: 0,
  void_orders: 0,
});

onMounted(async () => {
  const Chart = (await import("chart.js/auto")).default;

  // 1. Fetch today's summary
  const res = await api.get("/dashboard/today-summary");
  todaySummary.value = res.data;

  // 2. Prepare chart data for today only
  const today = new Date();
  const dateStr = today.toISOString().slice(0, 10); // YYYY-MM-DD

  const salesRes = await api.get(`/reports/daily-sales?date=${dateStr}`);
  labels.value = [dateStr];
  salesData.value = [salesRes.data.total_sales || 0];

  // 3. Build the chart
  const ctx = document.getElementById("salesChart") as HTMLCanvasElement;
  new Chart(ctx, {
    type: "bar",
    data: {
      labels: ["Total Sales"],
      datasets: [
        {
          label: "₱ Sales",
          data: [salesData.value[0]],
          backgroundColor: "#f7c948",
          borderRadius: 6,
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (context) => `₱${context.raw.toFixed(2)}`,
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          ticks: { color: "#999", callback: (v) => `₱${v}` },
          grid: { color: "#eee" },
        },
        x: {
          ticks: { color: "#999" },
          grid: { color: "#eee" },
        },
      },
    },
  });
});
</script>

<style scoped>
.main-layout {
  display: flex;
  height: 100vh;
  width: 100vw;
  overflow: hidden;
  font-family: "Segoe UI", "Arial", sans-serif;
  background: #f7f7fa;
}

.sidebar {
  width: 210px;
  background: #263143;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.sidebar-logo {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 78px;
  border-bottom: 1px solid #2d3952;
}
.sidebar-logo img {
  width: 46px;
  height: 46px;
  border-radius: 12px;
}
.sidebar-nav {
  flex: 1;
  padding-top: 20px;
}
.sidebar-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
}
.sidebar-nav li {
  padding: 12px 24px;
  cursor: pointer;
  display: flex;
  align-items: center;
  color: #b3c0d1;
  border-left: 4px solid transparent;
  transition: 0.2s background, 0.2s color, 0.2s border;
  margin-bottom: 6px;
}
.sidebar-nav li.active,
.sidebar-nav li:hover {
  background: #f7c948;
  color: #fff;
  border-left: 4px solid #fff;
}
.sidebar-nav span {
  font-size: 16px;
  font-weight: 500;
}

.content-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f8f9fa;
  min-width: 0;
}
.topbar {
  height: 48px;
  background: #263143;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  box-shadow: 0 2px 8px 0 #0001;
}
.topbar-left {
  display: flex;
  align-items: center;
}
.menu-icon {
  font-size: 22px;
  margin-right: 22px;
  cursor: pointer;
}
.topbar-right {
  display: flex;
  align-items: center;
}
.user-dropdown {
  display: flex;
  align-items: center;
  gap: 10px;
  background: #253145;
  border-radius: 7px;
  padding: 4px 20px;
}
.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid #fff3;
  background: #fff5;
}

.page-content {
  padding: 36px 28px 26px 28px;
  background: #fff;
  min-height: 0;
  flex: 1;
}
.breadcrumb-filter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 22px;
}
.breadcrumb {
  font-size: 15px;
  color: #9899a6;
  font-weight: 500;
  letter-spacing: 0.2px;
}
.dashboard-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}
.dashboard-filter select,
.dashboard-filter button {
  padding: 5px 14px;
  border-radius: 5px;
  border: 1px solid #cfd8e1;
  outline: none;
  font-size: 15px;
}
.dashboard-filter button {
  background: #22c1c3;
  color: #fff;
  font-weight: 600;
  border: none;
  cursor: pointer;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  grid-gap: 18px 22px;
  margin-bottom: 38px;
}
.dashboard-card {
  border-radius: 10px;
  padding: 24px 18px 18px 20px;
  color: #fff;
  box-shadow: 0 2px 5px 0 #ececec44;
  position: relative;
  min-width: 0;
}
.card-blue {
  background: #1a96c5; /* blue */
}
.card-red {
  background: #a41e22; /* red */
}
.card-yellow {
  background: #f7c948; /* yellow */
}
.card-cyan {
  background: #1dbfc1; /* cyan */
}
.card-purple {
  background: #8040ab; /* purple */
}
.card-cyan-light {
  background: #22c1c3;
  grid-column: 1 / 2;
  grid-row: 2;
}
.card-purple-light {
  background: #974ba6;
  grid-column: 2 / 3;
  grid-row: 2;
}
.card-red-light {
  background: #df7373;
  grid-column: 3 / 4;
  grid-row: 2;
}
.card-blue-light {
  background: #2da6d6;
  grid-column: 4 / 5;
  grid-row: 2;
}
.card-label {
  font-size: 2.1rem;
  font-weight: 700;
  margin-bottom: 3px;
}
.card-caption {
  font-size: 1.02rem;
  opacity: 0.9;
}

.dashboard-chart {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0px 2px 8px #eee6;
  padding: 22px 22px 18px 20px;
}
.chart-header {
  color: #22c1c3;
  font-size: 15.5px;
  margin-bottom: 12px;
  font-weight: 600;
  letter-spacing: 0.6px;
}
canvas {
  width: 100% !important;
  min-height: 220px;
  max-height: 280px;
  background: #fff;
  border-radius: 8px;
}

.sidebar-version {
  margin-top: auto;
  padding: 10px;
  font-size: 13px;
  text-align: center;
  color: #ccc;
}

/* Responsive styles */
@media (max-width: 900px) {
  .main-layout {
    flex-direction: column;
  }
  .sidebar {
    flex-direction: row;
    width: 100vw;
    height: 56px;
    min-width: 0;
    max-width: 100vw;
    align-items: center;
    border-bottom: 2px solid #1a2433;
    border-right: none;
    position: relative;
    z-index: 12;
    padding: 0;
  }
  .sidebar-logo {
    height: 56px;
    padding: 0 10px;
    border-bottom: none;
  }
  .sidebar-nav {
    flex: 1;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: flex-start;
  }
  .sidebar-nav ul {
    display: flex;
    flex-direction: row;
    width: 100vw;
    overflow-x: auto;
  }
  .sidebar-nav li {
    margin-bottom: 0;
    margin-right: 5px;
    padding: 10px 14px;
    border-left: none;
    border-bottom: 4px solid transparent;
  }
  .sidebar-nav li.active,
  .sidebar-nav li:hover {
    border-bottom: 4px solid #fff;
    border-left: none;
    background: #22c1c3;
  }
}

@media (max-width: 700px) {
  .dashboard-cards {
    grid-template-columns: 1fr 1fr;
    grid-gap: 16px 10px;
  }
  .dashboard-card {
    padding: 16px 10px 14px 14px;
    font-size: 1rem;
  }
  .page-content {
    padding: 18px 6px 12px 6px;
  }
  .topbar {
    padding: 0 12px;
    height: 42px;
  }
  .user-dropdown {
    padding: 4px 8px;
    font-size: 12px;
  }
  .chart-header {
    font-size: 13.5px;
    padding-bottom: 2px;
  }
  .breadcrumb-filter {
    flex-direction: column;
    gap: 10px;
    align-items: flex-start;
  }
  .dashboard-filter select,
  .dashboard-filter button {
    padding: 3px 7px;
    font-size: 13px;
  }
  .dashboard-filter {
    gap: 4px;
  }
}

@media (max-width: 500px) {
  .dashboard-cards {
    grid-template-columns: 1fr;
    grid-gap: 10px 0;
  }
  .dashboard-card {
    padding: 11px 5px 9px 10px;
    font-size: 0.92rem;
  }
  .topbar {
    padding: 0 4px;
    height: 36px;
    font-size: 13px;
  }
  .sidebar-logo img {
    width: 30px;
    height: 30px;
  }
}
</style>
