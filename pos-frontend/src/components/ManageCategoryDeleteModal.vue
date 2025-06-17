<template>
  <div class="modal-overlay" @click.self="closeModal">
    <div class="modal-box">
      <h2>Delete Category</h2>
      <p>
        Do you want to delete the category "<strong>{{
          categoryToDelete
        }}</strong
        >"?
      </p>
      <p>
        You can reassign its menu items to another category or delete them
        entirely.
      </p>

      <div class="input-group">
        <label>Reassign items to:</label>
        <select v-model="selectedCategory">
          <option value="">(Delete items)</option>
          <option v-for="cat in otherCategories" :key="cat" :value="cat">
            {{ cat }}
          </option>
        </select>
      </div>

      <div class="button-group">
        <button class="primary-btn" @click="confirmDelete">Confirm</button>
        <button class="secondary-btn" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  categoryToDelete: String,
  categories: Array,
});

const emits = defineEmits(["confirm", "close"]);
const closeModal = () => emits("close");

const selectedCategory = ref("");

const otherCategories = computed(() =>
  props.categories.filter((c) => c !== props.categoryToDelete)
);

function confirmDelete() {
  if (selectedCategory.value === props.categoryToDelete) {
    alert("Cannot reassign items to the same category being deleted.");
    return;
  }
  emits("confirm", {
    deleteCategory: props.categoryToDelete,
    reassignTo: selectedCategory.value,
  });
  emits("close");
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
  color: #222;
}

h2 {
  margin-bottom: 12px;
}

.input-group {
  margin: 16px 0;
}

select {
  background-color: #ffffff;
  color: #222;
}

select {
  width: 100%;
  padding: 8px;
  border-radius: 6px;
}

.button-group {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.primary-btn {
  background-color: #df4444;
  color: white;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
}

.secondary-btn {
  background-color: #ccc;
  color: #222;
  padding: 8px 14px;
  border: none;
  border-radius: 6px;
}
</style>
