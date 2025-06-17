import {
  createRouter,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";
import DashboardView from "./views/DashboardView.vue";
import MenuView from "./views/MenuView.vue";
import OrdersListView from "./views/OrdersListView.vue";
import SalesSummaryView from "./views/SalesSummaryView.vue";
import ReceiptView from "./views/ReceiptView.vue";
import CashierModernView from "./views/CashierModernView.vue";
import SupervisorToolsView from "./views/SupervisorToolsView.vue";

const routes = [
  { path: "/", redirect: "/cashier-modern" },
  {
    path: "/dashboard",
    component: DashboardView,
  },
  { path: "/menu", component: MenuView },
  { path: "/orders-list", name: "OrdersList", component: OrdersListView },
  {
    path: "/summary",
    name: "SalesSummary",
    component: SalesSummaryView,
  },
  {
    path: "/receipt/:orderId",
    name: "ReceiptView",
    component: ReceiptView,
  },
  {
    path: "/cashier-modern",
    name: "CashierModern",
    component: CashierModernView,
  },
  {
    path: "/supervisor-tools",
    name: "SupervisorTools",
    component: SupervisorToolsView,
  },
];

const router = createRouter({
  history:
    import.meta.env.MODE === "development"
      ? createWebHistory()
      : createWebHashHistory(),
  routes,
});

export default router;
