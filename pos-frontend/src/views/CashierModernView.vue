<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";
import { onMounted } from "vue";
import { useToast } from "vue-toastification";
import { computed } from "vue";
import api from "../axios";
import OrdersModal from "../components/OrdersModal.vue";
import OrderTypeModal from "../components/OrderTypeModal.vue";
import CommentsModal from "../components/CommentsModal.vue";
import PaymentModal from "../components/PaymentModal.vue";
import DiscountModal from "../components/DiscountModal.vue";
import DiscountDetailsModal from "../components/DiscountDetailsModal.vue";
import PinPromptModal from "../components/PinPromptModal.vue";
import CashierLoginModal from "../components/CashierLoginModal.vue";

const router = useRouter();
const toast = useToast();
const expandedCategory = ref([]);
const resumedOrderId = ref(null);
const cancelReason = ref("");
const showPinModal = ref(false);
const discountingItem = ref(null);
const showDiscountDetailsModal = ref(false);
const showResetConfirmModal = ref(false);
const cashierName = ref("");
const showCashierModal = ref(true);

const emit = defineEmits(["close", "select"]);

const handlePinSuccess = () => {
  showOrdersModal.value = true;
};

// Active tab tracking
const activeTab = ref("dashboard");

const closeModal = () => {
  emit("close");
};

const showCancelReasonModal = ref(false);
const showDashboardPinModal = ref(false);
const proceedToPaymentAfterOrderType = ref(false);
const showDiscountModal = ref(false);
const commentingItem = ref(null);
const showPaymentModal = ref(false);
const showCommentsModal = ref(false);

const availableCashiers = ["Cashier 1", "Cashier 2", "Cashier 3"];
const selectedCashier = ref("");
const isLoggedIn = ref(false);
const showCashierPinModal = ref(false);

// Show/hide functionality for orders modal
const showOrdersModal = ref(false);
const toggleOrdersModal = () => {
  showOrdersModal.value = !showOrdersModal.value;
};

// Discount Details
const handleDiscountDetailsProceed = (details) => {
  if (discountingItem.value) {
    discountingItem.value.discount_person_name = details.name;
    discountingItem.value.discount_person_id = details.idNumber;
    discountingItem.value.discount_person_type = details.discountType;
  }
  showDiscountModal.value = true;
};

// Show/hide functionality for order type modal
const showOrderTypeModal = ref(false);
const toggleOrderTypeModal = () => {
  showOrderTypeModal.value = !showOrderTypeModal.value;
  if (!showOrderTypeModal.value) {
    proceedToPaymentAfterOrderType.value = false;
  }
};

const applyVatToItem = (item) => {
  if (item.vat_applied) {
    toast.info("VAT already applied to this item.");
    return;
  }
  item.vat_applied = true;
  updateTotals();
};

const handleApplyDiscount = ({ type, value }) => {
  if (discountingItem.value) {
    discountingItem.value.manual_discount_type = type;
    discountingItem.value.manual_discount_value = value;
    discountingItem.value.final_price = calculateItemFinalPrice(
      discountingItem.value
    );
    updateTotals();
  }
  showDiscountModal.value = false;
};

const openItemCommentModal = (item) => {
  commentingItem.value = item;
  showCommentsModal.value = true;
};

const calculateItemFinalPrice = (item) => {
  let base = item.price;
  if (item.vat_applied) {
    base *= 100 / 112;
  }

  let total = base * item.quantity;

  if (item.manual_discount_type === "fixed") {
    total -= item.manual_discount_value;
  } else if (item.manual_discount_type === "percent") {
    total -= (item.manual_discount_value / 100) * total;
  }

  return Math.max(0, total);
};

// Handle order type selection
const selectOrderType = (type) => {
  console.log("Selected Order Type:", type);
  orderType.value = type;
  showOrderTypeModal.value = false;
  emit("select", type);
  closeModal();

  if (proceedToPaymentAfterOrderType.value) {
    proceedToPaymentAfterOrderType.value = false;
    showPaymentModal.value = true;
  }
};

// Right Side Menu
const groupedMenuItems = computed(() => {
  const categories = {};
  menuItems.value
    .filter((item) =>
      item.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    .forEach((item) => {
      if (!categories[item.category]) {
        categories[item.category] = [];
      }
      categories[item.category].push(item);
    });
  return categories;
});

// Dashboard redirect
const goToDashboard = () => {
  showDashboardPinModal.value = true;
};

const handleDashboardPinSuccess = () => {
  activeTab.value = "dashboard";
  router.push("/dashboard");
};

const resetConfirmed = () => {
  resetCart();
  showResetConfirmModal.value = false;
};

const cancelOrder = async (reason) => {
  try {
    await api.delete(
      `http://localhost:8000/orders/${resumedOrderId.value}/cancel`,
      {
        data: { cancel_reason: reason },
      }
    );

    toast.success(`Order #${resumedOrderId.value} canceled.`);
    resetCart();
    showCancelReasonModal.value = false;
    resumedOrderId.value = null;
  } catch (err) {
    toast.error("Failed to cancel the order.");
    console.error(err);
  }
};

// Active view mode
const viewMode = ref("grid");
const setViewMode = (mode) => {
  viewMode.value = mode;
};

// SearchBar
const searchQuery = ref("");

// Dummy data for demonstration
const customer = computed(() => {
  const discountTypes = cart.value
    .map((item) => item.discount_person_type)
    .filter(Boolean);

  return discountTypes.length > 0 ? discountTypes[0] : "Regular";
});

const orderType = ref("N/A");
const subtotal = ref(0);
const discount = ref(0);
const total = ref(0);

// Show/hide functionality for create category modal
const showCreateModal = ref(false);
const toggleCreateModal = () => {
  showCreateModal.value = !showCreateModal.value;
};

// Comment Modal
const customerComment = ref("");

const handleSaveComment = ({ comment }) => {
  if (commentingItem.value) {
    commentingItem.value.notes = comment;
    commentingItem.value = null;
  } else {
    customerComment.value = comment;
  }
  showCommentsModal.value = false;
};

const handleCheckout = async ({ paid, change, method }) => {
  if (!cart.value.length) {
    toast.error("Cart is empty.");
    return;
  }

  const items = cart.value.map((item) => ({
    menu_item_id: item.menu_item_id,
    quantity: item.quantity,
    discount_person_name: item.discount_person_name || null,
    discount_person_id: item.discount_person_id || null,
    discount_person_type: item.discount_person_type || null,
    manual_discount_type: item.manual_discount_type || null,
    manual_discount_value: item.manual_discount_value || 0,
    notes: item.notes || null,
  }));

  try {
    // 1. Create the order
    const res = await api.post("http://localhost:8000/orders/", {
      items,
      type: orderType.value,
      notes: customerComment.value,
      paid_amount: paid,
      discount: discount.value,
      cashier: selectedCashier.value,
    });

    const orderId = res.data.id;

    // 2. Mark it as paid using the /pay endpoint
    await api.post(`http://localhost:8000/orders/${orderId}/pay`, {
      paid,
    });

    // 3. Redirect to Receipt
    router.push({ name: "ReceiptView", params: { orderId } });

    // 4. Reset
    resetCart();
    customerComment.value = "";
    orderType.value = "N/A";
    showPaymentModal.value = false;
  } catch (err) {
    console.error("Checkout failed:", err.response?.data || err);
    toast.error("Failed to complete checkout.");
  }
};

const menuItems = ref([]);
const loading = ref(true);
const error = ref("");
const cart = ref([]);

const resetCart = () => {
  cart.value = [];
  subtotal.value = 0;
  discount.value = 0;
  total.value = 0;
};

// Button for Decreasing and Increasing Item Order Quantity
const decreaseQuantity = (item) => {
  if (item.quantity > 1) {
    item.quantity--;
  } else {
    cart.value = cart.value.filter((i) => i.menu_item_id !== item.menu_item_id);
  }
  updateTotals();
};

function increaseQuantity(item) {
  item.quantity++;
  updateTotals();
}

const openPaymentModal = () => {
  if (!cart.value.length) {
    toast.error("Cannot proceed: Cart is empty!");
    return;
  }

  if (!orderType.value || orderType.value === "N/A") {
    proceedToPaymentAfterOrderType.value = true;
    showOrderTypeModal.value = true;
  } else {
    showPaymentModal.value = true;
  }
};

const closePaymentModal = () => {
  showPaymentModal.value = false;
};

// Automatically recalculate when cart or discount changes
watch([cart, discount], () => {
  const sub = cart.value.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  subtotal.value = sub;
  total.value = sub - discount.value;
});

const holdOrder = async () => {
  if (!cart.value.length) {
    toast.error("Cart is empty.");
    return;
  }

  // Prevent holding a resumed order again
  if (resumedOrderId.value) {
    toast.info(`Order #${resumedOrderId.value} is already on hold.`);
    return;
  }

  const items = cart.value.map((item) => ({
    menu_item_id: item.menu_item_id,
    quantity: item.quantity,
  }));

  try {
    const res = await api.post("http://localhost:8000/orders/hold", {
      items,
      type: orderType.value,
      notes: customerComment.value,
      cashier: selectedCashier.value,
    });

    toast.success("Order held successfully!");

    resetCart();
    customerComment.value = "";
    orderType.value = "N/A";

    resumedOrderId.value = null;
    localStorage.removeItem("resumedOrder");
  } catch (err) {
    console.error("Failed to hold order:", err.response?.data || err);
    toast.error(
      err.response?.data?.detail?.[0]?.msg || "Failed to hold order."
    );
  }
};

function addToCart(item) {
  const existing = cart.value.find((i) => i.menu_item_id === item.id);
  if (existing) {
    existing.quantity++;
  } else {
    cart.value.push({
      menu_item_id: item.id,
      name: item.name,
      price: item.price,
      quantity: 1,
      vat_applied: false,
      manual_discount_type: null,
      manual_discount_value: 0,
      notes: "",
    });
  }
  updateTotals();
}

const openItemDiscountModal = (item) => {
  discountingItem.value = item;
  showDiscountDetailsModal.value = true;
};

function updateTotals() {
  let sub = 0;
  let discountTotal = 0;

  cart.value.forEach((item) => {
    const fullPrice = item.price * item.quantity;
    const finalPrice = calculateItemFinalPrice(item);
    discountTotal += fullPrice - finalPrice;
    sub += finalPrice;
  });

  subtotal.value = cart.value.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );
  discount.value = discountTotal;
  total.value = sub;
}

function handleResumeOrder(order) {
  // Clear the current cart
  cart.value = [];

  for (const item of order.items) {
    if (!item.menu_item) continue;

    cart.value.push({
      menu_item_id: item.menu_item.id,
      name: item.menu_item.name,
      price: item.menu_item.price,
      quantity: item.quantity,
      vat_applied: false,
      manual_discount_type: item.manual_discount_type || null,
      manual_discount_value: item.manual_discount_value || 0,
    });
  }

  orderType.value = order.type || "N/A";
  customerComment.value = order.notes || "";
  resumedOrderId.value = order.id;

  updateTotals();
  toast.info(`Resumed Order #${order.id}`);

  // Save to localStorage just in case user refreshes
  localStorage.setItem("resumedOrder", JSON.stringify(order));
}

// Cashier Selector Handler
const handleCashierPinSuccess = (name) => {
  if (name === "Supervisor") {
    router.push("/dashboard");
    return;
  }

  selectedCashier.value = name;
  cashierName.value = name;
  isLoggedIn.value = true;
  showCashierModal.value = false;

  // ✅ Save to localStorage
  localStorage.setItem("cashierName", name);

  toast.success(`${name} logged in`);
};

watch(isLoggedIn, (loggedIn) => {
  if (!loggedIn) {
    toast.warning("Please select a cashier and enter PIN to begin.");
  }
});

const logoutCashier = () => {
  toast.info(`${selectedCashier.value} logged out`);
  selectedCashier.value = "";
  cashierName.value = "";
  isLoggedIn.value = false;
  showCashierModal.value = true;

  // ✅ Clear from localStorage
  localStorage.removeItem("cashierName");
};

// Fetch menu
onMounted(async () => {
  try {
    const res = await api.get("http://localhost:8000/menu/");
    menuItems.value = res.data;
    console.log("Fetched menu items:", menuItems.value);

    const storedCashier = localStorage.getItem("cashierName");
    if (storedCashier) {
      selectedCashier.value = storedCashier;
      cashierName.value = storedCashier;
      isLoggedIn.value = true;
      showCashierModal.value = false;
    }

    // Resume order logic
    const resumed = localStorage.getItem("resumedOrder");
    if (resumed && cart.value.length === 0) {
      try {
        const order = JSON.parse(resumed);

        if (Array.isArray(order.items)) {
          cart.value = [];

          for (const item of order.items) {
            if (!item.menu_item) {
              console.warn(`Menu item missing for order item ID ${item.id}`);
              continue; // Skip missing items
            }

            cart.value.push({
              menu_item_id: item.menu_item.id,
              name: item.menu_item.name,
              price: item.menu_item.price,
              quantity: item.quantity,
              vat_applied: false,
              manual_discount_type: item.manual_discount_type || null,
              manual_discount_value: item.manual_discount_value || 0,
            });
          }
        }

        orderType.value = order.type || "N/A";
        customerComment.value = order.notes || "";
        resumedOrderId.value = order.id;

        updateTotals();
        toast.info(`Resumed Order #${order.id}`);
        router.replace("/cashier-modern");

        // ✅ Clear only after success
        localStorage.removeItem("resumedOrder");
      } catch (resumeErr) {
        console.error("Failed to process resumed order:", resumeErr);
        localStorage.removeItem("resumedOrder"); // 🔥 clear on failure too
        toast.error("Could not resume order. Please try again.");
      }
    }
  } catch (err) {
    error.value = "Failed to load menu.";
    console.error("Menu load error:", err);
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <CashierLoginModal
    v-if="showCashierModal"
    @success="handleCashierPinSuccess"
    @close="showCashierModal = false"
  />

  <template v-else>
    <div class="app-container">
      <div class="left-panel">
        <!-- Top Navigation Bar -->
        <div class="top-nav">
          <button
            class="nav-btn"
            :class="{ 'dashboard-btn': activeTab === 'dashboard' }"
            @click="goToDashboard"
          >
            <i class="fa-solid fa-gauge-high icon" /> Dashboard
          </button>

          <button
            class="nav-btn"
            :class="{ 'active-btn': activeTab === 'orders' }"
            @click="showPinModal = true"
          >
            <i class="fa-solid fa-clipboard-list icon" /> Orders
          </button>
          <button
            class="nav-btn"
            :class="{ 'active-btn': activeTab === 'orderType' }"
            @click="toggleOrderTypeModal"
          >
            <i class="fa-solid fa-clipboard-check icon" /> Order Type
          </button>
        </div>

        <!-- Secondary Navigation -->
        <div class="secondary-nav">
          <div class="cashier-status">
            <div class="cashier-info">
              <span class="cashier-label">Cashier: </span>
              <span class="cashier-name">{{
                selectedCashier || "Not Logged In"
              }}</span>
            </div>
            <button v-if="isLoggedIn" class="logout-btn" @click="logoutCashier">
              Logout
            </button>
          </div>
        </div>

        <!-- Product Table -->
        <div class="product-table">
          <div class="table-header">
            <div class="product-col">Product</div>
            <div class="quantity-col">Quantity</div>
            <div class="total-col">Total</div>
          </div>
          <div class="table-body">
            <div
              class="cart-item"
              v-for="item in cart"
              :key="item.menu_item_id"
            >
              <div class="product-col">
                {{ item.name }}
                <div class="product-actions">
                  <button class="vat-btn" @click="applyVatToItem(item)">
                    VAT
                  </button>
                  <button
                    class="discount-btn"
                    @click="openItemDiscountModal(item)"
                  >
                    Discount
                  </button>
                  <button
                    class="comment-btn"
                    @click="openItemCommentModal(item)"
                  >
                    Comment
                  </button>
                </div>
              </div>
              <button class="quantity-btn" @click="decreaseQuantity(item)">
                <i class="fa-solid fa-minus" />
              </button>
              <button class="quantity-btn" @click="increaseQuantity(item)">
                <i class="fa-solid fa-plus" />
              </button>
              <div class="quantity-col">x{{ item.quantity }}</div>
              <div class="total-col">
                ₱{{ calculateItemFinalPrice(item).toFixed(2) }}
              </div>
            </div>
          </div>
        </div>

        <!-- Order Summary -->
        <div class="order-summary">
          <div v-if="resumedOrderId" class="resumed-indicator">
            <i class="fa-solid fa-rotate-left"></i>
            Resumed Order #{{ resumedOrderId }}
          </div>
          <div class="summary-row">
            <div class="summary-label">Customer: {{ customer }}</div>
            <div class="summary-middle">Sub Total</div>
            <div class="summary-value">PHP{{ subtotal.toFixed(2) }}</div>
          </div>
          <div class="summary-row">
            <div class="summary-label">Type: {{ orderType }}</div>
            <div class="summary-middle">Discount</div>
            <div class="summary-value">PHP{{ discount.toFixed(2) }}</div>
          </div>
          <div class="summary-row total-row">
            <div class="summary-label" />
            <div class="summary-middle">Total</div>
            <div class="summary-value">PHP{{ total.toFixed(2) }}</div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="action-buttons">
          <button class="action-btn pay-btn" @click="openPaymentModal">
            <i class="fa-solid fa-credit-card icon" /> Pay
          </button>
          <button class="action-btn hold-btn" @click="holdOrder">
            <i class="fa-solid fa-pause icon" /> Hold
          </button>
        </div>
      </div>

      <div class="right-panel">
        <!-- Search and View Controls -->
        <div class="search-controls">
          <div class="search-box">
            <i class="fa-solid fa-magnifying-glass search-icon" />
            <input
              type="text"
              v-model="searchQuery"
              placeholder="Search menu..."
              class="search-input"
            />
          </div>
          <div class="view-controls">
            <button
              class="view-btn"
              :class="{ 'active-view': viewMode === 'grid' }"
              @click="setViewMode('grid')"
            >
              <i class="fa-solid fa-grip" />
            </button>
            <button
              class="view-btn"
              :class="{ 'active-view': viewMode === 'list' }"
              @click="setViewMode('list')"
            >
              <i class="fa-solid fa-bars" />
            </button>
          </div>
        </div>

        <!-- Menu Side (Right Side) -->
        <div class="menu-grid" :class="{ 'list-mode': viewMode === 'list' }">
          <div
            v-for="(items, category) in groupedMenuItems"
            :key="category"
            class="menu-category"
          >
            <div
              class="category-header"
              @click="
                expandedCategory =
                  expandedCategory === category ? null : category
              "
            >
              <h3>{{ category }}</h3>
              <i
                :class="[
                  'fa',
                  expandedCategory === category
                    ? 'fa-chevron-up'
                    : 'fa-chevron-down',
                ]"
              />
            </div>

            <div
              v-if="expandedCategory === category"
              class="category-items"
              :class="{ 'list-view': viewMode === 'list' }"
            >
              <div
                v-for="item in items"
                :key="item.id"
                class="menu-card"
                @click="addToCart(item)"
              >
                <img
                  v-if="item.image_url"
                  :src="item.image_url"
                  alt="item.name"
                />
                <p>
                  <strong>{{ item.name }}</strong>
                </p>
                <p>₱{{ item.price.toFixed(2) }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Create Category Modal -->
        <div v-if="showCreateModal" class="modal-overlay">
          <div class="modal-container">
            <div class="modal-header">
              <h3>Create Category</h3>
              <button class="close-btn" @click="toggleCreateModal">
                <i class="fa-solid fa-times" />
              </button>
            </div>
            <div class="modal-body">
              <div class="form-group">
                <label>Category Name</label>
                <input type="text" placeholder="Enter category name" />
              </div>
              <div class="form-group">
                <label>Description</label>
                <textarea placeholder="Enter description" />
              </div>
            </div>
            <div class="modal-footer">
              <button class="cancel-btn" @click="toggleCreateModal">
                Cancel
              </button>
              <button class="save-btn" @click="toggleCreateModal">Save</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div
      v-if="showResetConfirmModal"
      class="reset-modal-overlay"
      @click.self="showResetConfirmModal = false"
    >
      <div class="reset-modal-container">
        <h3 class="reset-modal-title">Confirm Void</h3>
        <p class="reset-modal-message">
          Are you sure you want to void the order?
        </p>
        <div class="reset-modal-footer">
          <button
            class="reset-btn cancel"
            @click="showResetConfirmModal = false"
          >
            Cancel
          </button>
          <button class="reset-btn confirm" @click="resetConfirmed">
            Confirm
          </button>
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
        <p>Enter a reason for canceling Order #{{ resumedOrderId }}</p>
        <textarea
          v-model="cancelReason"
          class="cancel-reason-textarea"
          placeholder="Enter cancel reason..."
        ></textarea>
        <div class="reset-modal-footer">
          <button
            class="reset-btn cancel"
            @click="showCancelReasonModal = false"
          >
            Close
          </button>
          <button class="reset-btn confirm" @click="cancelOrder(cancelReason)">
            Confirm Cancel
          </button>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <template v-if="showOrdersModal">
      <OrdersModal @close="toggleOrdersModal" @resume="handleResumeOrder" />
    </template>

    <PinPromptModal
      v-if="showPinModal"
      @close="showPinModal = false"
      @success="handlePinSuccess"
    />

    <PinPromptModal
      v-if="showDashboardPinModal"
      @close="showDashboardPinModal = false"
      @success="handleDashboardPinSuccess"
    />

    <OrderTypeModal
      v-if="showOrderTypeModal"
      @close="toggleOrderTypeModal"
      @select="selectOrderType"
    />

    <CommentsModal
      v-if="showCommentsModal"
      :commentText="commentingItem?.notes || customerComment"
      @close="showCommentsModal = false"
      @save="handleSaveComment"
    />

    <PaymentModal
      :show="showPaymentModal"
      :initial-total="total"
      :initial-sub-total="subtotal"
      :discount="discount"
      currency="₱"
      @close="closePaymentModal"
      @checkout="handleCheckout"
    />

    <DiscountModal
      v-if="showDiscountModal"
      @close="showDiscountModal = false"
      @apply="handleApplyDiscount"
    />

    <DiscountDetailsModal
      v-if="showDiscountDetailsModal"
      @close="showDiscountDetailsModal = false"
      @proceed="handleDiscountDetailsProceed"
    />
  </template>
</template>

<style src="../assets/cashier-modern.css"></style>
