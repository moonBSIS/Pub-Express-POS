<template>
  <div class="main-layout">
    <aside class="sidebar">
      <div class="sidebar-logo">
        <img src="../assets/logo.jpg" alt="Pub Express" />
      </div>
      <nav class="sidebar-nav">
        <ul>
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            custom
            v-slot="{ navigate, href, isActive }"
          >
            <li
              :class="{ active: isActive }"
              @click="navigate"
              :href="href"
              style="cursor: pointer"
            >
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
      <header class="topbar">Supervisor Tools</header>
      <div class="page-content">
        <div class="breadcrumb-filter">
          <div class="breadcrumb">Home &gt; Supervisor Tools</div>
        </div>

        <section
          class="dashboard-cards"
          style="
            display: flex;
            flex-direction: column;
            gap: 20px;
            max-width: 600px;
          "
        >
          <!-- Supervisor PIN -->
          <div
            class="dashboard-card card-red"
            style="min-width: 280px; max-width: 100%"
          >
            <div class="card-caption">Change Supervisor PIN</div>
            <input
              type="text"
              v-model="supervisorPin"
              placeholder="Enter new PIN"
              class="pin-input"
              style="background-color: azure; color: #222"
            />
            <button @click="updateSupervisorPin">Update PIN</button>
          </div>

          <!-- Combined Cashier Management -->
          <div
            class="dashboard-card card-yellow"
            style="min-width: 600px; max-width: 100%"
          >
            <div class="card-caption">Manage Cashiers</div>

            <div style="flex: 1; overflow-y: auto">
              <div
                v-for="(cashier, index) in cashiers"
                :key="index"
                class="cashier-row"
              >
                <input
                  :value="`Cashier ${index + 1}`"
                  disabled
                  class="cashier-input"
                  style="background-color: #f1f1f1; font-weight: bold"
                />
                <input
                  v-model="cashier.name"
                  placeholder="Real Name"
                  class="cashier-input"
                  style="background-color: azure; color: #222"
                />
                <input
                  v-model="cashier.pin"
                  placeholder="PIN"
                  type="text"
                  class="cashier-input"
                  style="background-color: azure; color: #222"
                />
                <button
                  v-if="cashier.id"
                  @click="deleteCashier(cashier.id)"
                  class="delete-btn"
                >
                  Delete
                </button>
              </div>
            </div>

            <button @click="addCashier">Add Cashier</button>
            <button @click="saveCashiers">Save All</button>
          </div>

          <!-- QR Code Link Config -->
          <div
            class="dashboard-card card-red"
            style="min-width: 280px; max-width: 100%; overflow-wrap: break-word"
          >
            <div class="card-caption">QR Code Link (For Receipt)</div>
            <input
              type="text"
              v-model="qrLink"
              placeholder="Enter link to encode as QR"
              class="pin-input"
              style="background-color: azure; color: #222"
            />
            <button @click="saveQrLink">Save QR Link</button>
          </div>

          <!-- Receipt Message Config -->
          <div
            class="dashboard-card card-yellow"
            style="min-width: 280px; max-width: 100%; overflow-wrap: break-word"
          >
            <div class="card-caption">Receipt Message (Footer)</div>
            <textarea
              v-model="receiptMessage"
              placeholder="Enter receipt footer message"
              rows="3"
              class="pin-input"
              style="resize: vertical; background-color: azure; color: #222"
            ></textarea>
            <button @click="saveReceiptMessage">Save Message</button>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import api from "../axios";
import { useToast } from "vue-toastification";

const appVersion = __APP_VERSION__;
const toast = useToast();
const qrLink = ref("");

const menuItems = [
  { name: "Cashier", path: "/cashier-modern" },
  { name: "Daily Sales", path: "/dashboard" },
  { name: "Reports", path: "/summary" },
  { name: "Menu", path: "/menu" },
  { name: "Orders", path: "/orders-list" },
  { name: "Supervisor Tools", path: "/supervisor-tools" },
];

const supervisorPin = ref("");
const cashiers = ref([]);

const fetchCashiers = async () => {
  try {
    const res = await api.get("/cashiers");
    cashiers.value = res.data.map((c) => ({
      id: c.id,
      name: c.name,
      pin: c.pin,
    }));
  } catch (err) {
    toast.error("Failed to load cashiers");
    console.error(err);
  }
};

const fetchSupervisor = async () => {
  const res = await api.get("/supervisors");
  if (res.data.length > 0) supervisorPin.value = res.data[0].pin;
};

const updateSupervisorPin = async () => {
  try {
    await api.put("/supervisors/1", { pin: supervisorPin.value });
    toast.success("Supervisor PIN updated");
  } catch (err) {
    toast.error("Failed to update supervisor PIN");
    console.error(err);
  }
};

const addCashier = () => {
  cashiers.value.push({ id: null, name: "", pin: "" });
};

const saveCashiers = async () => {
  try {
    let anySaved = false;
    for (const cashier of cashiers.value) {
      if (!cashier.name || !cashier.pin) {
        toast.warning("Please fill in both name and PIN for all cashiers.");
        return; // block entire save to enforce complete input
      }

      if (cashier.id) {
        await api.put(`/cashiers/${cashier.id}`, {
          name: cashier.name,
          pin: cashier.pin,
        });
      } else {
        const res = await api.post("/cashiers", {
          name: cashier.name,
          pin: cashier.pin,
        });
        cashier.id = res.data.id;
      }

      anySaved = true;
    }

    if (anySaved) {
      toast.success("Cashiers saved");
      await fetchCashiers(); // refresh list
    }
  } catch (err) {
    toast.error("Failed to save cashiers");
    console.error(err);
  }
};

const deleteCashier = async (id) => {
  if (!confirm("Delete this cashier?")) return;
  try {
    await api.delete(`/cashiers/${id}`);
    toast.success("Cashier deleted");
    await fetchCashiers();
  } catch (err) {
    toast.error("Failed to delete cashier");
    console.error(err);
  }
};

// Dynamic QR code

const fetchQrLink = async () => {
  try {
    const res = await api.get("/settings/qr-link");
    qrLink.value = res.data.value || "";
  } catch (err) {
    toast.error("Failed to load QR link");
    console.error(err);
  }
};

const saveQrLink = async () => {
  try {
    if (!qrLink.value.trim()) {
      toast.warning("QR link cannot be empty");
      return;
    }
    await api.put("/settings/qr-link", { value: qrLink.value });
    toast.success("QR link updated");
  } catch (err) {
    toast.error("Failed to update QR link");
    console.error(err);
  }
};

const receiptMessage = ref("");

const fetchReceiptMessage = async () => {
  try {
    const res = await api.get("/settings/receipt-message");
    receiptMessage.value = res.data.value || "";
  } catch (err) {
    toast.error("Failed to load receipt message");
    console.error(err);
  }
};

const saveReceiptMessage = async () => {
  try {
    await api.put("/settings/receipt-message", { value: receiptMessage.value });
    toast.success("Receipt message updated");
  } catch (err) {
    toast.error("Failed to update receipt message");
    console.error(err);
  }
};

onMounted(() => {
  fetchSupervisor();
  fetchCashiers();
  fetchQrLink();
  fetchReceiptMessage();
});
</script>

<style scoped>
.pin-input,
.cashier-input {
  width: 100%;
  padding: 10px;
  margin: 10px 0;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #ccc;
}

.cashier-row {
  display: grid;
  grid-template-columns: 120px 1fr 1fr auto;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

button {
  margin-top: 10px;
  padding: 10px;
  font-weight: bold;
  background-color: #ff7627;
  border: none;
  color: white;
  border-radius: 6px;
  cursor: pointer;
}

button:hover {
  background-color: #ff6702;
}

.cashier-input {
  flex: 1;
  padding: 8px;
  font-size: 14px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background-color: transparent;
}

.delete-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 12px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #dc2626;
}

.dashboard-card {
  display: flex;
  flex-direction: column;
  max-height: 300px;
  overflow-y: auto;
  padding-right: 10px;
}

.dashboard-cards {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
}

.sidebar-version {
  margin-top: auto;
  padding: 10px;
  font-size: 13px;
  text-align: center;
  color: #ccc;
}

/* Optional scrollbar styling for better UX */
.dashboard-card::-webkit-scrollbar {
  width: 6px;
}
.dashboard-card::-webkit-scrollbar-thumb {
  background-color: #ccc;
  border-radius: 3px;
}

@media (max-width: 900px) {
  .dashboard-cards {
    flex-direction: column;
  }
}
</style>
