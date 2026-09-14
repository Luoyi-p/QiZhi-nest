<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from "vue";
import { X } from "lucide-vue-next";
const props = defineProps<{ title: string; busy?: boolean }>();
const emit = defineEmits<{ close: [] }>();
const dialog = ref<HTMLDialogElement>();
const previousFocus = document.activeElement as HTMLElement | null;
onMounted(async () => {
  dialog.value?.showModal();
  await nextTick();
  dialog.value
    ?.querySelector<HTMLInputElement>("input, textarea, select")
    ?.focus();
});
onBeforeUnmount(() => {
  dialog.value?.close();
  previousFocus?.focus();
});
function close() {
  if (!props.busy) emit("close");
}
</script>

<template>
  <Teleport to="body">
    <dialog
      ref="dialog"
      class="modal"
      aria-labelledby="modal-title"
      @cancel.prevent="close"
    >
      <div class="modal-head">
        <div>
          <span class="eyebrow">YOUR PERSONAL SPACE</span>
          <h2 id="modal-title">{{ title }}</h2>
        </div>
        <button
          class="icon-button"
          aria-label="关闭"
          :disabled="busy"
          @click="close"
        >
          <X :size="20" />
        </button>
      </div>
      <slot />
    </dialog>
  </Teleport>
</template>
