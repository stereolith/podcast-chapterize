<template>
  <div class="relative">
    <div class="player-bar absolute bg-gray-400"></div>
    <div
      class="player-progress absolute bg-green-400 left-0"
      :style="{width: progress + '%'}">
      <span class="absolute right-0 text-gray-800">
        {{positionString}}
      </span>
      <!-- <ul class="token-list absolute right-0 bottom-0">
        <li 
          v-for="(token, index) in tokenList"
          :key="index"
          :style="{opacity: token.score *2}"
        >{{token.token}}</li>
      </ul> -->


    </div>

    <transition-group class="w-10" name="list-complete" tag="p">
      <span
        v-for="(token, index) in tokenList"
        :key="index"
        class="list-complete-item"
        :style="{opacity: token.score *2}"
      >
        {{ token.token }}
      </span>
    </transition-group>
  </div>
</template>

<script>


export default {
  name: 'PlayerBar',
  props: ['duration', 'position', 'tokenList', 'chapterBoundaries'],
  data () {
    return {
    }
  },
  mounted() {

  },
  computed: {
    progress () {
      return this.position / this.duration * 100
    },
    positionString () {
      let mins = this.position > 60 ? Math.floor(this.position/60) : '00'
      return `${mins}:${(this.position % 60).toString().padStart(2,0)}`
    }
  }
}
</script>

<style scoped lang="scss">
.player-bar {
  height: 2px;
  width: 100%;
}
.player-progress {
  height: 2px;
  span {
    transform: translateX(50%);
    font-size: 14px;
    padding-top: 4px;
  }
}
.token-list {
  transform: translateX(50%);
  text-align: center;
}

.list-complete-item {
  transition: all 1s;
  display: inline-block;
  margin-right: 10px;
}
.list-complete-enter, .list-complete-leave-to
/* .list-complete-leave-active below version 2.1.8 */ {
  opacity: 0;
  transform: translateY(30px);
}
.list-complete-leave-active {
  position: absolute;
}
</style>