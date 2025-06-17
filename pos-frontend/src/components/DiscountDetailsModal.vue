<script setup>
import { ref } from "vue";
import { useToast } from "vue-toastification";

const emit = defineEmits(["close", "proceed"]);
const toast = useToast();
const discountType = ref("Senior Citizen");
const name = ref("");
const idNumber = ref("");

const handleProceed = () => {
  if (!name.value.trim()) {
    toast.error(`Please Enter a Name`);
    return;
  }
  emit("proceed", {
    discountType: discountType.value,
    name: name.value,
    idNumber: idNumber.value,
  });
  emit("close");
};
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Discount Details</h3>
        <button class="close-btn" @click="$emit('close')">
          <i class="fa-solid fa-xmark" />
        </button>
      </div>

      <div class="modal-body">
        <div class="input-group">
          <label>Discount Type</label>
          <select v-model="discountType" class="input-field">
            <option>Senior Citizen</option>
            <option>PWD</option>
            <option>Employee</option>
            <option>Owner</option>
            <option>Coupon</option>
          </select>
        </div>

        <div class="input-group">
          <label>Name <span style="color: red">*</span></label>
          <input
            v-model="name"
            type="text"
            placeholder="Enter full name"
            class="input-field"
            required="true"
          />
        </div>

        <div class="input-group">
          <label>ID Number</label>
          <input
            v-model="idNumber"
            type="text"
            placeholder="Enter ID number"
            class="input-field"
          />
        </div>
      </div>

      <div class="modal-footer">
        <button class="cancel-btn" @click="$emit('close')">Cancel</button>
        <button class="proceed-btn" @click="handleProceed">Proceed</button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
}

.modal-container {
  background: white;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-width: 90%;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.modal-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #888;
}

.modal-body {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-weight: bold;
  margin-bottom: 5px;
  color: #444;
}

.input-field {
  padding: 8px 10px;
  border-radius: 5px;
  border: 1px solid #ccc;
  background-color: transparent;
  color: #222;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.cancel-btn,
.proceed-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 5px;
  font-weight: bold;
  cursor: pointer;
}

.cancel-btn {
  background-color: #ddd;
  color: #333;
}

.proceed-btn {
  background-color: #4ade80;
  color: white;
}

.proceed-btn:hover {
  background-color: #22c55e;
}
</style>
