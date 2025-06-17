<script setup>
import { ref, watch } from "vue";
import { useRouter } from "vue-router";

const router = useRouter();

const props = defineProps({
  show: { type: Boolean, default: false },
  initialTotal: { type: Number, default: 0 },
  initialSubTotal: { type: Number, default: 0 },
  discount: { type: Number, default: 0 },
  currency: { type: String, default: "₱" },
});

const emit = defineEmits(["close", "payment-complete", "checkout"]);

const activeTab = ref("Cash");
const paid = ref(0.0);
const change = ref(0.0);
const screen = ref(0.0);

const total = ref(props.initialTotal);
const discount = ref(props.initialSubTotal - props.initialTotal);

// Watch if props.initialTotal changes
watch(
  () => props.initialTotal,
  (val) => {
    total.value = val;
    discount.value = props.initialSubTotal - val;
  }
);

watch(
  () => props.initialSubTotal,
  (val) => {
    discount.value = val - props.initialTotal;
  }
);

watch(
  () => props.discount,
  (val) => {
    discount.value = val || 0;
  }
);

watch(
  () => props.show,
  (newVal) => {
    document.body.classList.toggle("modal-open", newVal);
  }
);

const paymentOptions = [
  { id: "cash", label: "Cash" },
  { id: "bank", label: "Bank Payment" },
  { id: "account", label: "Customer Account" },
  { id: "paymentList", label: "Payment List", count: 0 },
];

const closeModal = () => emit("close");

const switchTab = (tab) => {
  activeTab.value = tab;
};

const addToScreen = (value) => {
  let current = screen.value.toString();
  if (current === "0" || current === "0.00") current = "";

  if (value === "<") {
    current = current.slice(0, -1);
    screen.value = parseFloat(current) || 0;
  } else if (value === "→") {
    paid.value = parseFloat(current) || 0;
    change.value = paid.value > total.value ? paid.value - total.value : 0;
    screen.value = 0; // Clear screen but don't submit yet
  } else {
    current += value;
    screen.value = parseFloat(current) || 0;
  }
};

const checkout = () => {
  if (!paid.value && screen.value) {
    paid.value = parseFloat(screen.value.toString()) || 0;
  }

  change.value = paid.value > total.value ? paid.value - total.value : 0;
  screen.value = 0;

  emit("checkout", {
    paid: paid.value,
    change: change.value,
    method: activeTab.value,
  });
};

watch([paid, total], () => {
  change.value = paid.value > total.value ? paid.value - total.value : 0;
});
</script>

<template>
  <div v-if="show" class="modal-overlay">
    <div class="modal">
      <div class="modal-header">
        <h2>Gateway : {{ activeTab }}</h2>
        <button class="close-button" @click="closeModal">×</button>
      </div>
      <div class="modal-content">
        <div class="main-content">
          <div class="info-row">
            <div class="info-box info-box-blue">
              <span>Total :</span>
              <span class="amount">{{ currency }}{{ total.toFixed(2) }}</span>
            </div>
            <div class="info-box info-box-red">
              <span>Discount :</span>
              <span class="amount"
                >{{ currency }}{{ discount.toFixed(2) }}</span
              >
            </div>
          </div>

          <div class="info-row">
            <div class="info-box info-box-green">
              <span>Paid :</span>
              <span class="amount">{{ currency }}{{ paid.toFixed(2) }}</span>
            </div>
            <div class="info-box info-box-yellow">
              <span>Change :</span>
              <span class="amount">{{ currency }}{{ change.toFixed(2) }}</span>
            </div>
          </div>

          <div class="info-row">
            <div class="info-box info-box-gray">
              <span>Screen :</span>
              <span class="amount">{{ currency }}{{ screen.toFixed(2) }}</span>
            </div>
          </div>

          <div class="numpad">
            <div class="numpad-button" @click="addToScreen('7')">7</div>
            <div class="numpad-button" @click="addToScreen('8')">8</div>
            <div class="numpad-button" @click="addToScreen('9')">9</div>
            <div class="numpad-button" @click="addToScreen('4')">4</div>
            <div class="numpad-button" @click="addToScreen('5')">5</div>
            <div class="numpad-button" @click="addToScreen('6')">6</div>
            <div class="numpad-button" @click="addToScreen('1')">1</div>
            <div class="numpad-button" @click="addToScreen('2')">2</div>
            <div class="numpad-button" @click="addToScreen('3')">3</div>
            <div class="numpad-button" @click="addToScreen('<')">⌫</div>
            <div class="numpad-button" @click="addToScreen('0')">0</div>
            <div class="numpad-button" @click="addToScreen('→')">→</div>
          </div>

          <button
            class="full-payment-button"
            :disabled="paid < total"
            @click="checkout"
          >
            Checkout
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
body.modal-open {
  overflow: hidden;
}

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
  width: 100vw;
  height: 100vh;
}

.modal {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background-color: #fff;
  border-radius: 4px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  width: 95vw;
  max-width: 1100px;
  max-height: 90vh;
  overflow-y: auto;
  z-index: 1050;
  display: flex;
  flex-direction: column;
}

.modal-content {
  display: flex;
  flex: 1;
  flex-direction: row;
  flex-wrap: wrap;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  background-color: #e9ecef;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 500;
  color: #343a40;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: #6c757d;
}

.modal-content {
  display: flex;
  flex: 1;
  flex-direction: row;
  flex-wrap: wrap;
}

.payment-badge {
  display: inline-block;
  background-color: #28a745;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  text-align: center;
  line-height: 24px;
  margin-left: 10px;
  font-size: 0.85rem;
}

.main-content {
  flex: 1;
  padding: 15px;
}

.info-row {
  display: flex;
  margin-bottom: 10px;
}

.info-box {
  flex: 1;
  padding: 15px;
  margin: 0 5px;
  border-radius: 4px;
  display: flex;
  justify-content: space-between;
  font-size: 1.1rem;
}

.info-box-blue {
  background-color: #cfe2ff;
  color: #084298;
}

.info-box-red {
  background-color: #f8d7da;
  color: #842029;
}

.info-box-green {
  background-color: #d1e7dd;
  color: #0f5132;
}

.info-box-yellow {
  background-color: #fff3cd;
  color: #664d03;
}

.info-box-gray {
  background-color: #e9ecef;
  color: #343a40;
}

.amount {
  font-weight: bold;
}

.numpad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 20px;
}

.numpad-button {
  background-color: #fff;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  padding: 20px;
  font-size: 1.5rem;
  cursor: pointer;
  text-align: center;
  color: #555;
}

.numpad-button:hover {
  background-color: #f8f9fa;
}

.full-payment-button {
  background-color: #4ade80;
  color: #fff;
  border: none;
  border-radius: 4px;
  padding: 15px;
  margin-top: 20px;
  font-size: 1.1rem;
  cursor: pointer;
  width: 100%;
}

.full-payment-button:hover {
  background-color: #22c55e;
}

.full-payment-button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .modal {
    width: 100vw;
    height: 100vh;
    max-width: none;
    max-height: 95vh;
    border-radius: 0;
    transform: none;
    top: 0;
    left: 0;
    flex-direction: column;
  }

  .modal-content {
    flex-direction: column;
    flex-wrap: nowrap;
    overflow-x: auto;
  }
}
</style>
