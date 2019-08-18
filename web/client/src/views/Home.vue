<template>
  <div class="container mx-auto">
    <h1 class="text-xl text-center mb-4 mt-3">podcast-chapterize</h1>
    <p>Automatically annotate a podcast epidose with ID3 chapter markers, powered by natural language processing that identify topic changes. Just enter a feed url, choose an episode and press start!</p>
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
