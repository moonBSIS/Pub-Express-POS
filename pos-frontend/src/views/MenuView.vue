<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo.jpg" alt="Pub Express" />
      </div>
      <nav class="sidebar-nav">
        <ul>
          <router-link
            v-for="item in menuNavItems"
            :key="item.path"
            :to="item.path"
            custom
            v-slot="{ navigate, href, isActive }"
          >
            <li :class="{ active: isActive }" @click="navigate" :href="href">
              {{ item.name }}
            </li>
          </router-link>
        </ul>
      </nav>
      <div class="sidebar-version">
        <small>v{{ appVersion }}</small>
      </div>
    </aside>

    <div class="content-wrapper">
      <header class="topbar">
        Menu Management
        <div class="add-buttons">
          <button @click="startNewItem">+ Add Item</button>
          <button @click="startNewCategory">+ Add Category</button>
        </div>
      </header>

      <div class="page-content">
        <!-- Category Filters -->
        <div class="filter-categories">
          <button
            :class="{ active: selectedCategory === '' }"
            @click="selectedCategory = ''"
          >
            All
          </button>
          <button
            v-for="cat in categories"
            :key="cat"
            :class="{ active: selectedCategory === cat }"
          >
            <span @click="selectedCategory = cat">{{ cat }}</span>
            <span
              @click.stop="deleteCategory(cat)"
              style="margin-left: 8px; cursor: pointer"
              title="Delete category"
            >
              <i
                class="fa-solid fa-trash"
                style="color: red; font-size: 16px"
              ></i>
            </span>
          </button>
        </div>

        <div class="search-bar">
          <input v-model="searchQuery" placeholder="Search menu..." />
        </div>

        <div v-if="loading">Loading menu...</div>
        <div v-else class="dashboard-cards">
          <div
            v-for="item in filteredItems"
            :key="item.id"
            class="dashboard-card card-yellow"
          >
            <img
              v-if="item.image_url"
              :src="item.image_url"
              class="menu-thumb"
            />
            <h3>{{ item.name }}</h3>
            <p>₱{{ item.price.toFixed(2) }}</p>
            <p class="small">{{ item.category }}</p>
            <div class="menu-buttons">
              <button @click="startEdit(item)">Edit</button>
              <button @click="deleteItem(item.id)">Delete</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <EditItemModal
      v-if="editingItem"
      :item="editingItem"
      :categories="categories"
      @saved="fetchMenu"
      @close="editingItem = null"
    />

    <AddCategoryModal
      v-if="showAddCategory"
      :existingCategories="categories"
      @added="handleCategoryAdded"
      @removed="deleteCategory"
      @close="showAddCategory = false"
    />

    <ManageCategoryDeleteModal
      v-if="categoryToDelete"
      :categoryToDelete="categoryToDelete"
      :categories="categories"
      @confirm="handleCategoryDeletion"
      @close="categoryToDelete = null"
    />

    <ItemDeleteConfirmModal
      v-if="itemToDelete"
      :itemName="itemToDelete.name"
      @confirm="confirmDeleteItem"
      @close="itemToDelete = null"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import api from "../axios";
import { useToast } from "vue-toastification";
import EditItemModal from "../components/EditItemModal.vue";
import AddCategoryModal from "../components/AddCategoryModal.vue";
import ManageCategoryDeleteModal from "../components/ManageCategoryDeleteModal.vue";
import ItemDeleteConfirmModal from "../components/ItemDeleteConfirmModal.vue";

const appVersion = __APP_VERSION__;
const toast = useToast();
const menuItems = ref([]);
const categories = ref([]);
const selectedCategory = ref("");
const searchQuery = ref("");

const loading = ref(true);
const showAddCategory = ref(false);
const categoryToDelete = ref(null);

const editingItem = ref(null);
const itemToDelete = ref(null);

async function fetchMenu() {
  loading.value = true;
  const res = await api.get("/menu/");
  menuItems.value = res.data;
  categories.value = [...new Set(res.data.map((i) => i.category))];
  loading.value = false;
}

function deleteItem(id) {
  const item = menuItems.value.find((i) => i.id === id);
  itemToDelete.value = item;
}

async function confirmDeleteItem() {
  try {
    await api.delete(`/menu/${itemToDelete.value.id}`);
    toast.success(`"${itemToDelete.value.name}" deleted successfully.`);
    await fetchMenu();
  } catch (err) {
    toast.error("Failed to delete item.");
  } finally {
    itemToDelete.value = null;
  }
}

function startEdit(item) {
  editingItem.value = { ...item };
}

function startNewItem() {
  editingItem.value = {
    name: "",
    category: "",
    price: null,
    image_url: "",
  };
}

function startNewCategory() {
  showAddCategory.value = true;
}

function handleCategoryAdded(newCat) {
  categories.value.push(newCat);
  toast.success(`Category "${newCat}" added.`);
}

const filteredItems = computed(() => {
  return menuItems.value
    .filter(
      (i) => !selectedCategory.value || i.category === selectedCategory.value
    )
    .filter((i) =>
      i.name.toLowerCase().includes(searchQuery.value.toLowerCase())
    );
});

function deleteCategory(cat) {
  categoryToDelete.value = cat;
}

async function handleCategoryDeletion({ deleteCategory, reassignTo }) {
  if (!confirm(`Proceed with deleting "${deleteCategory}"?`)) return;

  await api.post("/menu/delete-category", {
    category: deleteCategory,
    reassign_to: reassignTo,
  });

  await fetchMenu();
  categoryToDelete.value = null;

  if (reassignTo) {
    toast.success(
      `Category "${deleteCategory}" deleted. Items reassigned to "${reassignTo}".`
    );
  } else {
    toast.success(`Category "${deleteCategory}" and its items deleted.`);
  }
}

onMounted(() => {
  fetchMenu();
});

const menuNavItems = [
  { name: "Cashier", path: "/cashier-modern" },
  { name: "Daily Sales", path: "/dashboard" },
  { name: "Reports", path: "/summary" },
  { name: "Menu", path: "/menu" },
  { name: "Orders", path: "/orders-list" },
  { name: "Supervisor Tools", path: "/supervisor-tools" },
];
</script>

<style scoped>
@import "../assets/dashboardview.css";

.menu-thumb {
  width: 100%;
  height: 140px;
  object-fit: cover;
  border-radius: 8px;
  margin-bottom: 10px;
}

.filter-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.filter-categories button {
  background-color: #cecece;
  border-radius: 20px;
  padding: 6px 12px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  color: #222;
}

.filter-categories button.active {
  background-color: #f7c948; /* Pub Express yellow */
  color: #222;
  font-weight: 600;
}

.filter-categories button i {
  margin-left: 4px;
}

.search-bar {
  margin-bottom: 20px;
}

.search-bar input {
  width: 100%;
  padding: 8px 14px;
  border-radius: 20px;
  border: 1px solid #ccc;
  font-size: 15px;
  background-color: transparent;
  color: #222;
}

.search-bar input::placeholder {
  color: #aaa;
}

.dashboard-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 14px;
}

.dashboard-card {
  background-color: #f7c948; /* Yellow cards */
  padding: 16px;
  border-radius: 10px;
  box-shadow: 0 2px 5px #ccc;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  color: #222; /* Dark text */
  text-align: center;
}

.dashboard-card h3 {
  font-size: 1.1rem;
  margin-bottom: 6px;
}

.dashboard-card p {
  margin: 4px 0;
}

.menu-buttons {
  margin-top: 8px;
  display: flex;
  gap: 6px;
}

.menu-buttons button {
  background-color: #333;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.menu-buttons button:hover {
  background-color: #555;
}

/* Topbar buttons */
.add-buttons button {
  background-color: #df4444; /* Accent red */
  color: white;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  cursor: pointer;
  margin-left: 8px;
}

.add-buttons button:hover {
  background-color: #c43b3b;
}

.sidebar-version {
  margin-top: auto;
  padding: 10px;
  font-size: 13px;
  text-align: center;
  color: #ccc;
}
</style>
