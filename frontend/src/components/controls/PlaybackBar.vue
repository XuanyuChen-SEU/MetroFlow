<template>
  <div class="control-bar">
    <div class="time-tag">{{ `${hour.toString().padStart(2, "0")}:00` }}</div>
    <input :value="hour" min="0" max="23" type="range" @input="$emit('update:hour', Number($event.target.value))" />
    <button class="ghost-btn" @click="$emit('toggle')">{{ playing ? "暂停" : "播放" }}</button>
  </div>
</template>

<script setup>
defineProps({
  hour: Number,
  playing: Boolean,
});

defineEmits(["update:hour", "toggle"]);
</script>
