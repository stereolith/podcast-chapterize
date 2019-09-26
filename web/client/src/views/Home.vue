<template>
  <div class="container mx-auto px-2">
    <h1 class="text-xl text-center mb-4 mt-3">podcast-chapterize</h1>
    <p class="">Automatically annotate a podcast epidose with ID3 chapter markers, powered by natural language processing that identify topic changes. Just enter a feed url, choose an episode and press start!</p>
    <p>When a process is started, it is saved to browser storage and is loaded when site is reopened.</p>
    <ChapterizePanel />
  </div>
</template>

<script>
import ChapterizePanel from '@/components/ChapterizePanel.vue'

export default {
  name: 'home',
  components: {
    ChapterizePanel
  }
}
</script>

<style>
.container {
  max-width: 768px !important; 
}
</style>
