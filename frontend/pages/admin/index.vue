<template>
  <div class="dashboard">
    <template #title>
      <h1>Dashboard</h1>
    </template>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon stat-icon--blue">📋</div>
        <div class="stat-content">
          <p class="stat-label">Preguntas activas</p>
          <p class="stat-value">—</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon--green">👥</div>
        <div class="stat-content">
          <p class="stat-label">Estudiantes</p>
          <p class="stat-value">—</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon--purple">📝</div>
        <div class="stat-content">
          <p class="stat-label">Exámenes realizados</p>
          <p class="stat-value">—</p>
        </div>
      </div>

      <div class="stat-card">
        <div class="stat-icon stat-icon--orange">✅</div>
        <div class="stat-content">
          <p class="stat-label">Tasa de aprobación</p>
          <p class="stat-value">—</p>
        </div>
      </div>
    </div>

    <div class="dashboard-section">
      <h2>Actividad reciente</h2>
      <p class="empty-state">No hay actividad reciente para mostrar.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: 'admin',
  middleware: ['auth'],
})
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.stat-icon--blue { background: #eff6ff; }
.stat-icon--green { background: #f0fdf4; }
.stat-icon--purple { background: #faf5ff; }
.stat-icon--orange { background: #fff7ed; }

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0 0 0.25rem;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin: 0;
}

.dashboard-section {
  background: white;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
  padding: 1.25rem;
}

.dashboard-section h2 {
  font-size: 1rem;
  font-weight: 600;
  color: #111827;
  margin: 0 0 1rem;
}

.empty-state {
  color: #9ca3af;
  font-size: 0.875rem;
  text-align: center;
  padding: 2rem 0;
  margin: 0;
}
</style>
