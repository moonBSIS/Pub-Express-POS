<script setup>
import { ref, watch } from "vue";

const emit = defineEmits(["close", "apply"]);
const props = defineProps(["show"]);

const discountType = ref("fixed");
const discountValue = ref(0);
const screen = ref("0");

const formattedValue = ref("");

watch(discountValue, (val) => {
  if (discountType.value === "percent") {
    formattedValue.value = `${val}%`;
  } else {
    formattedValue.value = `₱${val}`;
  }
});

watch(discountType, () => {
  discountValue.value = 0;
  screen.value = "0";
});

const addToScreen = (val) => {
  if (val === "<") {
    screen.value = screen.value.slice(0, -1) || "0";
  } else if (val === "-") {
    screen.value = screen.value.startsWith("-")
      ? screen.value.slice(1)
      : `-${screen.value}`;
  } else {
    if (screen.value === "0") {
      screen.value = val;
    } else {
      screen.value += val;
    }
  }
  discountValue.value = parseFloat(screen.value) || 0;
};

const closeModal = () => emit("close");

const applyDiscount = () => {
  emit("apply", {
    type: discountType.value,
    value: discountValue.value,
  });
  closeModal();
};
</script>

<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Apply Discount</h3>
        <button class="close-btn" @click="closeModal">
          <i class="fa-solid fa-xmark" />
        </button>
      </div>

      <div class="modal-body">
        <div class="type-toggle">
          <button
            :class="{ active: discountType === 'fixed' }"
            @click="discountType = 'fixed'"
          >
            Fixed (₱)
          </button>
          <button
            :class="{ active: discountType === 'percent' }"
            @click="discountType = 'percent'"
          >
            Percent (%)
          </button>
        </div>

        <div class="input-group">
          <label
            >Discount {{ discountType === "percent" ? "(%)" : "(₱)" }}</label
          >
          <input
            type="number"
            v-model.number="discountValue"
            placeholder="Enter amount"
            min="0"
          />
          <small class="note">{{ formattedValue }}</small>
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
        <div class="numpad-button" @click="addToScreen('-')">±</div>
        <div class="numpad-button" @click="addToScreen('0')">0</div>
        <div class="numpad-button" @click="addToScreen('<')">⌫</div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="closeModal">Cancel</button>
        <button class="apply-btn" @click="applyDiscount">Apply</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  border-radius: 8px;
  width: 400px;
  padding: 20px;
  box-shadow: 0 5px 20px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-body {
  margin-top: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}

.type-toggle {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.type-toggle button {
  flex: 1;
  padding: 10px;
  cursor: pointer;
  border: 1px solid #ccc;
  background: #f8f9fa;
  border-radius: 4px;
  font-weight: 500;
  color: #555;
}

.type-toggle button.active {
  background: #4ade80;
  color: white;
  border-color: #4ade80;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.note {
  color: #888;
  font-size: 0.9rem;
  margin-top: 5px;
}

.cancel-btn,
.apply-btn {
  padding: 10px 15px;
  border-radius: 4px;
  border: none;
  font-weight: 500;
}

.cancel-btn {
  background: #ddd;
}

.apply-btn {
  background: #4ade80;
  color: white;
}
.numpad {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  margin-top: 20px;
}

.numpad-button {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 6px;
  padding: 18px;
  font-size: 1.25rem;
  text-align: center;
  cursor: pointer;
  transition: background 0.2s;
}

.numpad-button:hover {
  background-color: #f1f5f9;
}
</style>
