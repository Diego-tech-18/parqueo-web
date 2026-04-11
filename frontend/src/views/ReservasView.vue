<template>
  <div class="layout">

       <SidebarNav :abierto="sidebarAbierto" @toggle="sidebarAbierto = !sidebarAbierto" />
  </div>
</template>

<script setup>
import '@/assets/css/usuarios.css'
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import SidebarNav from '@/components/SidebarNav.vue'
import UsuarioForm from '@/components/forms/UsuarioForm.vue'
</script>