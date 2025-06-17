<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <div class="modal-content">
      <h3>{{ item?.id ? "Edit Menu Item" : "Add New Menu Item" }}</h3>

      <div class="modal-body">
        <label>Name</label>
        <input v-model="formData.name" type="text" placeholder="Name" />

        <label>Category</label>
        <select v-model="formData.category" required class="input-like">
          <option v-for="cat in categories" :key="cat" :value="cat">
            {{ cat }}
          </option>
          <option disabled value="">Select a category</option>
        </select>

        <label>Price (₱)</label>
        <input
          v-model.number="formData.price"
          type="number"
          placeholder="Price"
          min="0"
        />
      </div>

      <div class="modal-footer">
        <button
          class="btn-save"
          @click="saveItem"
          :disabled="!formData.name || !formData.category || !formData.price"
        >
          Save
        </button>
        <button class="btn-cancel" @click="$emit('close')">Cancel</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from "vue";
import api from "../axios";
import { useToast } from "vue-toastification";

const toast = useToast();
const props = defineProps({
  item: Object,
  categories: Array,
});

const emit = defineEmits(["saved", "close"]);
const closeModal = () => emit("close");

const formData = ref({
  name: "",
  category: "",
  price: null,
});

// Watch for prop changes (editing existing item or new item)
watch(
  () => props.item,
  (newItem) => {
    if (newItem) {
      formData.value = {
        name: newItem.name || "",
        category: newItem.category || "",
        price: newItem.price || null,
      };
    } else {
      formData.value = {
        name: "",
        category: "",
        price: null,
      };
    }
  },
  { immediate: true }
);

async function saveItem() {
  try {
    if (
      !formData.value.name ||
      !formData.value.category ||
      formData.value.price === null
    ) {
      toast.error("Please fill in all required fields.");
      return;
    }

    if (props.item && props.item.id) {
      // Update existing item
      await api.put(`/menu/${props.item.id}`, {
        name: formData.value.name,
        category: formData.value.category,
        price: formData.value.price,
      });
      toast.success("Item updated.");
    } else {
      // Create new item
      await api.post(`/menu/`, {
        name: formData.value.name,
        category: formData.value.category,
        price: formData.value.price,
      });
      toast.success("Item added.");
    }

    emit("saved");
    emit("close");
  } catch (err) {
    if (err.response?.status === 400 && err.response?.data?.detail) {
      toast.error(err.response.data.detail);
    } else {
      toast.error("Failed to save item.");
    }
    console.error(err);
  }
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal-container {
  background: #fff;
  padding: 20px;
  border-radius: 10px;
  width: 400px;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 18px;
  cursor: pointer;
}

.modal-content {
  background-color: #fff;
  padding: 24px;
  border-radius: 12px;
  width: auto;
  max-width: 400px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  flex-direction: column;
  gap: 10px;
}

h3 {
  margin-bottom: 18px;
  font-size: 1.3rem;
  color: #333;
}

.modal-body label {
  display: block;
  margin-top: 10px;
  margin-bottom: 5px;
  font-weight: 500;
  color: #333;
}

.modal-body input,
.modal-body select {
  width: 100%;
  padding: 10px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #fafafa;
  color: #333;
  font-size: 14px;
}

.modal-body input:focus {
  border-color: #22c1c3;
  outline: none;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 20px;
}

.input-like {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border-radius: 6px;
  border: 1px solid #ccc;
  font-size: 15px;
  background-color: white;
  color: #333;
}

.btn-save {
  background-color: #22c1c3;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}

.btn-save:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.btn-cancel {
  background-color: #ccc;
  color: #333;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: bold;
  cursor: pointer;
}

.preview-img {
  margin-top: 8px;
  max-width: 100%;
  max-height: 150px;
  border-radius: 6px;
}

.combo-row {
  display: flex;
  gap: 8px;
  margin-top: 8px;
  align-items: center;
}

.combo-row select {
  flex: 1;
}

.combo-row input {
  width: 60px;
}

button {
  padding: 6px 12px;
  border-radius: 4px;
  border: none;
  background-color: #df4444;
  color: white;
  cursor: pointer;
}

button:hover {
  background-color: #c23333;
}
</style>
