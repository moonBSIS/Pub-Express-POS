<template>
  <div class="modal-overlay">
    <div class="modal-box">
      <h3>Are you sure you want to delete "{{ itemName }}"?</h3>
      <div class="button-group">
        <button class="primary-btn" @click="$emit('confirm')">
          Yes, Delete
        </button>
        <button class="secondary-btn" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  itemName: String,
});
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-box {
  background: white;
  padding: 24px;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  color: #333;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.primary-btn {
  background-color: #df4444;
  color: white;
  padding: 8px 14px;
  border-radius: 6px;
}

.secondary-btn {
  background-color: #ccc;
  padding: 8px 14px;
  border-radius: 6px;
}
</style>
