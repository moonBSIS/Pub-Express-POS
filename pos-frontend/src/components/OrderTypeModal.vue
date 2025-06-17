<script setup>
import { ref } from "vue";

const emit = defineEmits(["close", "select"]);

// Selected order type
const selectedType = ref("");

// Close the modal
const closeModal = () => {
  emit("close");
};

// Select an order type
const selectOrderType = (type) => {
  selectedType.value = type;
  emit("select", type);
  closeModal();
};
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Define The Order Type</h3>
      </div>

      <div class="order-types">
        <div
          class="order-type-option"
          :class="{ selected: selectedType === 'Dine-in' }"
          @click="selectOrderType('Dine-in')"
        >
          <div class="option-image takeaway-img">
            <img src="../assets/dine-in.svg" alt="Dine-in" />
          </div>
          <div class="option-text">Dine-in</div>
        </div>

        <div
          class="order-type-option"
          :class="{ selected: selectedType === 'Take-out' }"
          @click="selectOrderType('Take-out')"
        >
          <div class="option-image delivery-img">
            <img src="../assets/take-out.svg" alt="Take-out" />
          </div>
          <div class="option-text">Take-out</div>
        </div>
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
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
  font-weight: 500;
}

.order-types {
  display: flex;
  flex-wrap: wrap;
}

.order-type-option {
  flex: 1 0 50%;
  min-width: 150px;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid #eee;
}

.order-type-option:hover {
  background-color: #f8f9fa;
}

.order-type-option.selected {
  background-color: #e3f2fd;
  border-color: #2196f3;
}

.option-image {
  width: 80px;
  height: 80px;
  margin-bottom: 10px;
  display: flex;
  justify-content: center;
  align-items: center;
  overflow: hidden;
}

.option-image img,
.option-image svg {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.option-text {
  font-size: 16px;
  font-weight: 500;
  color: #333;
}

/* Custom colors for SVG icons */
.takeaway-img svg {
  width: 100%;
  height: 100%;
}

.delivery-img svg {
  width: 100%;
  height: 100%;
}
</style>
