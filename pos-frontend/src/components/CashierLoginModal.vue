<template>
  <div class="modal-overlay">
    <div class="modal-container" :class="{ shake: wrongPin }">
      <h2 class="modal-title">Login</h2>

      <select v-model="selectedCashier" class="pin-input">
        <option disabled value="">Select Cashier</option>
        <option
          v-for="cashier in cashierList"
          :key="cashier.id"
          :value="cashier.name"
        >
          Cashier {{ cashier.id }} - {{ cashier.name }}
        </option>
        <option value="Supervisor">Supervisor</option>
      </select>

      <input
        type="password"
        v-model="pin"
        placeholder="Enter PIN"
        class="pin-input"
        @keyup.enter="submitPin"
      />

      <p v-if="error" class="error">{{ error }}</p>

      <div class="buttons">
        <button class="submit" @click="submitPin">Login</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../axios";

const emit = defineEmits(["success", "close"]);

const pin = ref("");
const error = ref("");
const wrongPin = ref(false);
const selectedCashier = ref("");
const cashierList = ref([]);
const supervisorPin = ref("");

// Fetch both cashier list and supervisor PIN on mount
onMounted(async () => {
  try {
    const cashiersRes = await api.get("/cashiers");
    cashierList.value = cashiersRes.data;

    const supRes = await api.get("/supervisors");
    if (supRes.data.length > 0) {
      supervisorPin.value = supRes.data[0].pin;
    }
  } catch (err) {
    error.value = "Failed to load credentials.";
    console.error(err);
  }
});

const submitPin = async () => {
  if (!selectedCashier.value) {
    error.value = "Please select a role.";
    return;
  }

  if (selectedCashier.value === "Supervisor") {
    if (pin.value === supervisorPin.value) {
      emit("success", "Supervisor");
      emit("close");
      pin.value = "";
      error.value = "";
      wrongPin.value = false;
      return;
    } else {
      error.value = "Incorrect Supervisor PIN.";
      wrongPin.value = true;
      setTimeout(() => (wrongPin.value = false), 500);
      return;
    }
  }

  // Validate as Cashier
  const cashier = cashierList.value.find(
    (c) => c.name === selectedCashier.value
  );

  if (!cashier) {
    error.value = "Cashier not found.";
    return;
  }

  try {
    const pinRes = await api.get(`/cashiers/${cashier.id}`);
    if (pin.value === pinRes.data.pin) {
      emit("success", cashier.name);
      emit("close");
      pin.value = "";
      error.value = "";
      wrongPin.value = false;
    } else {
      error.value = "Incorrect PIN.";
      wrongPin.value = true;
      setTimeout(() => (wrongPin.value = false), 500);
    }
  } catch (err) {
    error.value = "Error validating cashier PIN.";
    console.error(err);
  }
};
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
}

.modal-container {
  background: #f9fafb;
  padding: 25px 20px;
  border-radius: 10px;
  width: 320px;
  text-align: center;
  box-shadow: 0px 10px 25px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
}

.modal-title {
  margin-bottom: 15px;
  font-size: 20px;
  font-weight: 700;
  color: #1f2937;
}

.pin-input {
  width: 100%;
  padding: 12px;
  margin: 10px 0 10px;
  font-size: 18px;
  border: 1px solid #ccc;
  border-radius: 6px;
  background: white;
  color: #111827;
}

.error {
  color: #ef4444;
  font-size: 14px;
  margin: 5px 0 15px;
}

.buttons {
  display: flex;
  justify-content: space-between;
  margin-top: 10px;
  width: 100%;
  min-width: 350px;
}

.cancel {
  background: #e5e7eb;
  color: #374151;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.submit {
  background: #4ade80;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}

.cancel:hover {
  background: #d1d5db;
}

.submit:hover {
  background: #22c55e;
}

/* Shake animation for wrong pin */
@keyframes shake {
  0% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-8px);
  }
  50% {
    transform: translateX(8px);
  }
  75% {
    transform: translateX(-8px);
  }
  100% {
    transform: translateX(0);
  }
}

.shake {
  animation: shake 0.4s;
}
</style>
