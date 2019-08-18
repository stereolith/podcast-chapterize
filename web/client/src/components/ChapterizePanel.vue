<template>
<div class="border rounded-lg shadow-md p-4 my-10 bg-white">
  <div class="flex flex-col">

    <ChooseEpisode />

    <button class="px-4 py-2 mt-8 bg-pink-400 rounded text-white font-bold w-1/3 self-center">Start</button> 
  
  </div>
</div>
</template>

<script>
import ProgressBar from './ProgressBar'
import ChooseEpisode from './ChooseEpisode'

export default {
  name: 'ChapterizePanel',
  components: {
    ProgressBar,
    ChooseEpisode
  },
  data () {
    return {
      feedUrl: '',
      
    }
  }
}
</script>
