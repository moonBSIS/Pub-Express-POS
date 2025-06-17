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
      <header class="topbar">Sales Reports</header>
      <div class="page-content">
        <div class="breadcrumb-filter">
          <div class="breadcrumb">Home &gt; Summary</div>
          <div class="date-range">
            <input type="date" v-model="startDate" />
            <span>to</span>
            <input type="date" v-model="endDate" />
            <button @click="fetchSummary">Go</button>
            <button @click="exportXLSX" class="csv-button">Export Excel</button>
          </div>
        </div>
        <section class="dashboard-cards">
          <div class="dashboard-card card-red">
            <div class="card-label">₱{{ summary.total_paid.toFixed(2) }}</div>
            <div class="card-caption">Total Sales</div>
          </div>
          <div class="dashboard-card card-yellow">
            <div class="card-label">
              ₱{{ summary.total_discount.toFixed(2) }}
            </div>
            <div class="card-caption">Total Discounts</div>
          </div>
          <div class="dashboard-card card-red">
            <div class="card-label">{{ summary.orders_paid }}</div>
            <div class="card-caption">Total Orders</div>
          </div>
          <div class="dashboard-card card-yellow">
            <div class="card-label">{{ summary.dine_in_count }}</div>
            <div class="card-caption">Dine-in Orders</div>
          </div>
          <div class="dashboard-card card-yellow">
            <div class="card-label">{{ summary.take_out_count }}</div>
            <div class="card-caption">Take-out Orders</div>
          </div>
          <div class="dashboard-card card-red">
            <div class="card-label">
              ₱{{ summary.dine_in_sales.toFixed(2) }}
            </div>
            <div class="card-caption">Dine-in Sales</div>
          </div>
          <div class="dashboard-card card-yellow">
            <div class="card-label">
              ₱{{ summary.take_out_sales.toFixed(2) }}
            </div>
            <div class="card-caption">Take-out Sales</div>
          </div>
          <div class="dashboard-card card-red">
            <div class="card-label">{{ summary.void_orders }}</div>
            <div class="card-caption">Orders Void</div>
          </div>
        </section>

        <div class="charts-row">
          <section class="dashboard-chart chart-half">
            <div class="chart-header">
              SALES CHART ( {{ startDate }} - {{ endDate }} )
            </div>
            <canvas id="summaryChart" />
          </section>

          <section class="dashboard-chart chart-half">
            <div class="chart-header">
              Item Sales Chart ( {{ startDate }} - {{ endDate }} )
            </div>
            <select
              v-model="selectedMenuItemId"
              class="item-select"
              @change="fetchItemSales"
            >
              <option
                v-for="item in allMenuItems"
                :key="item.id"
                :value="item.id"
              >
                {{ item.name }}
              </option>
            </select>
            <canvas id="itemSalesChart" />
          </section>
        </div>

        <div class="charts-row">
          <section class="dashboard-chart chart-half">
            <div class="chart-header">
              Top Items Ranking ( {{ startDate }} - {{ endDate }} )
            </div>
            <canvas id="rankingChart" />
          </section>

          <section class="dashboard-chart chart-half">
            <div class="chart-header">
              Top Discounts Used ( {{ startDate }} - {{ endDate }} )
            </div>
            <canvas id="discountChart" />
          </section>
        </div>
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

let summaryChartInstance = null;
let itemChartInstance = null;
let rankingChartInstance = null;
let discountChartInstance = null;

const startDate = ref<string>(new Date().toISOString().slice(0, 10));
const endDate = ref<string>(new Date().toISOString().slice(0, 10));

const summary = ref({
  total_paid: 0,
  total_discount: 0,
  orders_paid: 0,
  orders_unpaid: 0,
  dine_in_count: 0,
  dine_in_sales: 0,
  take_out_count: 0,
  take_out_sales: 0,
  void_orders: 0,
});

const averageOrderValue = ref(0);
const averageDiscountPerOrder = ref(0);

const labels = ref<string[]>([]);
const salesData = ref<number[]>([]);
const topItems = ref<any[]>([]);
const discountUsage = ref<any[]>([]);
const discountLabels = ref<string[]>([]);
const discountData = ref<number[]>([]);

const bestDay = ref({ date: "-", amount: 0 });

async function fetchSummary() {
  const menuRes = await api.get("/menu/");
  allMenuItems.value = menuRes.data;

  if (!selectedMenuItemId.value && allMenuItems.value.length > 0) {
    selectedMenuItemId.value = allMenuItems.value[0].id;
    await fetchItemSales();
  }

  const discountTypes = discountUsage.value.map((d) => d.type || "None");
  const discountCounts = discountUsage.value.map((d) => d.count || 0);

  // Save for chart rendering
  discountLabels.value = discountTypes;
  discountData.value = discountCounts;
  renderDiscountChart();

  // 1. Summary data
  const res = await api.get("/summary/range", {
    params: { start_date: startDate.value, end_date: endDate.value },
  });
  summary.value = res.data;

  // Calculate AOV and average discount/order
  averageOrderValue.value = summary.value.orders_paid
    ? summary.value.total_paid / summary.value.orders_paid
    : 0;

  averageDiscountPerOrder.value = summary.value.orders_paid
    ? summary.value.total_discount / summary.value.orders_paid
    : 0;

  // 3. Sales chart data
  const dateLabels: string[] = [];
  const salesTotals: number[] = [];

  const start = new Date(startDate.value);
  const end = new Date(endDate.value);

  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().slice(0, 10);
    const salesRes = await api.get(`/reports/daily-sales?date=${dateStr}`);
    dateLabels.push(dateStr);
    salesTotals.push(salesRes.data.total_sales || 0);
  }

  labels.value = dateLabels;
  salesData.value = salesTotals;

  // 4. Calculate Best Day by Sales
  const maxSales = Math.max(...salesTotals);
  const index = salesTotals.indexOf(maxSales);
  bestDay.value = {
    date: index >= 0 ? dateLabels[index] : "-",
    amount: maxSales,
  };

  // 5. Top items
  const topRes = await api.get("/reports/top-items", {
    params: { start_date: startDate.value, end_date: endDate.value },
  });
  topItems.value = topRes.data;

  // 6. Discount usage
  const discountRes = await api.get("/reports/discount-usage");
  discountUsage.value = discountRes.data;

  // 7. Render chart
  renderChart();
  renderRankingChart();
  renderDiscountChart();
}

async function exportXLSX() {
  try {
    const res = await api.get("/reports/orders-xlsx", {
      params: {
        start_date: startDate.value,
        end_date: endDate.value,
      },
      responseType: "blob",
    });

    const blob = new Blob([res.data], {
      type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `PubExpress_Sales_Report_${startDate.value}_to_${endDate.value}.xlsx`;
    link.click();
  } catch (error) {
    console.error("Excel export failed:", error);
    alert("Failed to export Excel file. Please try again.");
  }
}

async function renderChart() {
  const Chart = (await import("chart.js/auto")).default;
  const ctx = document.getElementById("summaryChart") as HTMLCanvasElement;

  if (summaryChartInstance) summaryChartInstance.destroy();

  summaryChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels.value,
      datasets: [
        {
          label: "Sales",
          data: salesData.value,
          borderColor: "#a41e22",
          backgroundColor: "#a41e22",
          fill: true,
          tension: 0.3,
          pointBackgroundColor: "#df4444",
        },
      ],
    },
    options: { responsive: true },
  });
}

// New variables for item sales chart
const allMenuItems = ref<any[]>([]);
const selectedMenuItemId = ref<number | null>(null);
const itemSalesLabels = ref<string[]>([]);
const itemSalesData = ref<Record<number, number[]>>({});

async function fetchItemSales() {
  if (!selectedMenuItemId.value) return;

  const dateLabels: string[] = [];
  const salesTotals: number[] = [];

  const start = new Date(startDate.value);
  const end = new Date(endDate.value);

  for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
    const dateStr = d.toISOString().slice(0, 10);

    const res = await api.get("/reports/item-sales", {
      params: {
        date: dateStr,
        item_id: selectedMenuItemId.value,
      },
    });

    dateLabels.push(dateStr);
    salesTotals.push(res.data.total_sales || 0);
  }

  itemSalesLabels.value = dateLabels;
  itemSalesData.value = salesTotals;

  renderItemChart();
}

async function renderItemChart() {
  const Chart = (await import("chart.js/auto")).default;
  const ctx = document.getElementById("itemSalesChart") as HTMLCanvasElement;

  if (itemChartInstance) itemChartInstance.destroy();

  itemChartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: itemSalesLabels.value,
      datasets: [
        {
          label: "Item Sales",
          data: itemSalesData.value,
          borderColor: "#df4444",
          backgroundColor: "#df4444",
        },
      ],
    },
    options: {
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          ticks: { color: "#999" },
          grid: { color: "#eee" },
        },
        y: { ticks: { color: "#999" } },
      },
    },
  });
}

async function renderRankingChart() {
  const Chart = (await import("chart.js/auto")).default;
  const ctx = document.getElementById("rankingChart") as HTMLCanvasElement;

  if (rankingChartInstance) rankingChartInstance.destroy();

  rankingChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: topItems.value.map((item) => item.item),
      datasets: [
        {
          label: "Total Sold",
          data: topItems.value.map((item) => item.total_sold),
          backgroundColor: "#f7c948",
        },
      ],
    },
    options: {
      indexAxis: "y",
      responsive: true,
      scales: {
        x: {
          beginAtZero: true,
          ticks: { color: "#999" },
          grid: { color: "#eee" },
        },
        y: { ticks: { color: "#999" } },
      },
    },
  });
}

async function renderDiscountChart() {
  const Chart = (await import("chart.js/auto")).default;
  const ctx = document.getElementById("discountChart") as HTMLCanvasElement;

  if (discountChartInstance) discountChartInstance.destroy();

  discountChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: discountLabels.value,
      datasets: [
        {
          data: discountData.value,
          backgroundColor: [
            "#a41e22",
            "#f7c948",
            "#e67e22",
            "#1abc9c",
            "#9b59b6",
          ],
        },
      ],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "right",
          labels: { color: "#333" },
        },
      },
    },
  });
}

onMounted(() => {
  fetchSummary();
});
</script>

<style src="../assets/salessummaryview.css"></style>
