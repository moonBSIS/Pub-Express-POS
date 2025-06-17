<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-box">
      <h2>Add New Category</h2>

      <input
        v-model="newCategory"
        type="text"
        placeholder="New category name"
        class="input-field"
      />
      <div class="button-group">
        <button class="primary-btn" @click="submit">Add Category</button>
        <button class="secondary-btn" @click="$emit('close')">Close</button>
      </div>

      <hr style="margin: 16px 0" />

      <h3 style="margin-top: 20px">Existing Categories</h3>
      <div class="category-list">
        <div v-for="cat in existingCategories" :key="cat" class="category-item">
          {{ cat }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

const props = defineProps({
  existingCategories: Array,
});

const emits = defineEmits(["added", "removed", "close", "delete", "close"]);

const newCategory = ref("");
const closeModal = () => emits("close");

function submit() {
  if (!newCategory.value.trim()) return;

  // Prevent duplicate
  if (
    props.existingCategories.some(
      (c) => c.toLowerCase() === newCategory.value.trim().toLowerCase()
    )
  ) {
    alert("This category already exists.");
    return;
  }

  emits("added", newCategory.value.trim());
  newCategory.value = "";
}
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
  z-index: 2000;
}

.modal-box {
  background: white;
  padding: 24px;
  border-radius: 12px;
  width: 400px;
  max-width: 90%;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

h2 {
  margin-bottom: 14px;
  font-size: 20px;
  color: #263143;
}

h3 {
  margin-top: 14px;
  font-size: 16px;
  color: #444;
}

.input-field {
  width: 100%;
  padding: 10px 14px;
  border-radius: 8px;
  border: 1px solid #ccc;
  background-color: transparent;
  font-size: 15px;
  margin-bottom: 16px;
  color: #222;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.primary-btn {
  background-color: #22c1c3;
  color: white;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.secondary-btn {
  background-color: #ccc;
  color: #222;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.category-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid #ddd;
  padding: 8px;
  border-radius: 8px;
  margin-top: 10px;
}

.category-item {
  display: flex;
  justify-content: space-between;
  padding: 4px 0;
}

.category-list li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin: 6px 0;
  padding: 4px 0;
}

.delete-btn {
  background-color: #df4444;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 4px 8px;
  cursor: pointer;
  font-size: 12px;
}

.category-list {
  color: #222;
}
</style>
