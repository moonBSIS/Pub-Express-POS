<script setup>
import { ref, onMounted, watch } from "vue";
import api from "../axios";
import { computed } from "vue";
import { useToast } from "vue-toastification";
import { useRouter } from "vue-router";
const router = useRouter();

const emit = defineEmits(["close", "resume"]);

const activeTab = ref("onHold");
const setActiveTab = (tab) => {
  activeTab.value = tab;
};

const heldOrders = ref([]);
const loading = ref(false);
const paidOrders = ref([]);
const error = ref("");
const showCancelReasonModal = ref(false);
const cancelReason = ref("");
const cancelingOrderId = ref(null);
const searchQuery = ref("");
const toast = useToast();

const promptCancel = (orderId) => {
  cancelingOrderId.value = orderId;
  cancelReason.value = "";
  showCancelReasonModal.value = true;
};

const cancelOrder = async (reason) => {
  try {
    await api.delete(`/orders/${cancelingOrderId.value}/cancel`, {
      data: { cancel_reason: reason },
    });
    toast.success(`Order #${cancelingOrderId.value} was canceled.`);
    showCancelReasonModal.value = false;
    fetchOrders();
  } catch (err) {
    console.error("Failed to cancel order:", err);
    toast.error("Failed to cancel the order.");
  }
};

const fetchOrders = async () => {
  try {
    loading.value = true;

    const heldRes = await api.get("/orders?status=held");
    heldOrders.value = heldRes.data;

    const paidRes = await api.get("/orders?is_paid=true");
    paidOrders.value = paidRes.data;
  } catch (err) {
    error.value = "Failed to fetch orders.";
    console.error(err);
  } finally {
    loading.value = false;
  }
};

const filteredHeldOrders = computed(() => {
  return heldOrders.value.filter((order) =>
    `${order.id} ${order.type ?? ""} ${order.cashier ?? ""}`
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
  );
});

const filteredPaidOrders = computed(() => {
  return paidOrders.value.filter((order) =>
    `${order.id} ${order.type ?? ""} ${order.cashier ?? ""}`
      .toLowerCase()
      .includes(searchQuery.value.toLowerCase())
  );
});

const closeModal = () => {
  emit("close");
};

const resumeOrder = (order) => {
  emit("resume", order);
  emit("close");
  // localStorage.setItem("resumedOrder", JSON.stringify(order));
  // router.replace({ name: "CashierModern" });
};

onMounted(() => {
  fetchOrders();

  watch(activeTab, () => {
    fetchOrders();
  });
});
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Orders</h3>
        <button class="close-btn" @click="closeModal">
          <i class="fa-solid fa-xmark" />
        </button>
      </div>

      <div class="tabs">
        <button
          class="tab-btn"
          :class="{ 'active-tab': activeTab === 'onHold' }"
          @click="setActiveTab('onHold')"
        >
          On Hold
        </button>
        <button
          class="tab-btn"
          :class="{ 'active-tab': activeTab === 'paid' }"
          @click="setActiveTab('paid')"
        >
          Paid
        </button>
      </div>

      <div class="search-bar">
        <input
          type="text"
          v-model="searchQuery"
          placeholder="Search..."
          class="search-input"
        />
        <button class="search-btn">
          <i class="fa-solid fa-magnifying-glass" />
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loading">Loading...</div>
        <div v-else>
          <template v-if="activeTab === 'onHold' && heldOrders.length">
            <div
              class="order-item"
              v-for="order in filteredHeldOrders"
              :key="order.id"
            >
              <div>
                <strong>Order #{{ order.id }}</strong
                ><br />
                {{ order.type }} • Handled by: {{ order.cashier || "Unknown" }}
              </div>
              <div class="order-actions">
                <button @click="resumeOrder(order)">Resume</button>
                <button
                  @click="promptCancel(order.id)"
                  style="background-color: #f87171; margin-left: 10px"
                >
                  Void
                </button>
              </div>
            </div>
          </template>

          <template v-else-if="activeTab === 'paid' && paidOrders.length">
            <div
              class="order-item"
              v-for="order in filteredPaidOrders"
              :key="order.id"
            >
              <div>
                <strong>Order #{{ order.id }}</strong
                ><br />
                {{ order.type }} • Handled by: {{ order.cashier || "Unknown" }}
              </div>
              <div class="order-actions">
                <button @click="resumeOrder(order)">Edit</button>
                <button
                  @click="promptCancel(order.id)"
                  style="background-color: #f87171; margin-left: 10px"
                >
                  Void
                </button>
              </div>
            </div>
          </template>

          <div v-else class="empty-state">
            <p>Nothing to display...</p>
          </div>
        </div>
      </div>

      <div class="modal-footer">
        <button class="close-modal-btn" @click="closeModal">Close</button>
      </div>
    </div>
  </div>

  <div
    v-if="showCancelReasonModal"
    class="reset-modal-overlay"
    @click.self="showCancelReasonModal = false"
  >
    <div class="reset-modal-container">
      <h3 class="reset-modal-title">Cancel Order</h3>
      <p>Enter a reason for canceling Order #{{ cancelingOrderId }}</p>
      <textarea
        v-model="cancelReason"
        class="cancel-reason-textarea"
        placeholder="Enter cancel reason..."
      ></textarea>
      <div class="reset-modal-footer">
        <button class="reset-btn cancel" @click="showCancelReasonModal = false">
          Close
        </button>
        <button class="reset-btn confirm" @click="cancelOrder(cancelReason)">
          Confirm Cancel
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-container {
  background-color: white;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
  border-radius: 8px;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
  color: #888;
}

.close-btn:hover {
  color: #333;
}

.tabs {
  display: flex;
  border-bottom: 1px solid #eee;
}

.tab-btn {
  flex: 1;
  padding: 10px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: #555;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
}

.tab-btn:hover {
  background-color: #f8f9fa;
}

.active-tab {
  border-bottom: 3px solid #4285f4;
  color: #4285f4;
  font-weight: 500;
}

.search-bar {
  display: flex;
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.search-input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-btn {
  padding: 8px 15px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
}

.modal-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  min-height: 200px;
  color: #333;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: #888;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px 20px;
  border-top: 1px solid #eee;
}

.close-modal-btn {
  padding: 8px 15px;
  background-color: #4285f4;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.close-modal-btn:hover {
  background-color: #3b77db;
}

.order-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  margin-bottom: 10px;
  border: 1px solid #eee;
  border-radius: 6px;
  background-color: #f9f9f9;
}

.order-item button {
  padding: 6px 10px;
  background-color: #4ade80;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.order-actions {
  display: flex;
  gap: 8px;
}

button.danger {
  background-color: #ef4444;
}
</style>
