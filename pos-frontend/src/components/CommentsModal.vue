<script setup>
import { ref, watch } from "vue";
import { useToast } from "vue-toastification";

const emit = defineEmits(["close", "save"]);
const toast = useToast();

const props = defineProps({
  commentText: {
    type: String,
    default: "",
  },
  showOnReceiptInitial: {
    type: Boolean,
    default: false,
  },
});

// Comment content and display toggle
const comment = ref(props.commentText);

// If props change while open (optional but safe)
watch(
  () => props.commentText,
  (newVal) => {
    comment.value = newVal;
  }
);

// Close modal
const closeModal = () => {
  emit("close");
};

// Save and emit values
const saveComment = () => {
  emit("save", { comment: comment.value });
  toast.info(`Comment Added`);
  closeModal();
};
</script>

<template>
  <div class="modal-overlay">
    <div class="modal-container">
      <div class="modal-header">
        <h3>Add Comments</h3>
      </div>

      <div class="modal-body">
        <textarea
          v-model="comment"
          rows="4"
          placeholder="Enter customer comments (e.g. extra spicy, no mayo)..."
          style="
            width: 100%;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
            background-color: transparent;
            color: #333;
          "
        ></textarea>
      </div>

      <div class="modal-footer">
        <button @click="closeModal" class="cancel-btn">Cancel</button>
        <button @click="saveComment" class="save-btn">Save</button>
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
  color: #333 !important;
  font-weight: 500;
}

.modal-body {
  padding: 20px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px 20px;
  border-top: 1px solid #eee;
  gap: 10px;
}

.cancel-btn,
.save-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
}

.cancel-btn {
  background-color: #f1f1f1;
  color: #333;
}

.save-btn {
  background-color: #4285f4;
  color: white;
}

.cancel-btn:hover {
  background-color: #e5e5e5;
}

.save-btn:hover {
  background-color: #3b77db;
}

label {
  color: #555;
}
</style>
