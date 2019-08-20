<template>
  <div class="status-bar w-100 flex">
    <div
      v-for="(state, index) in states"
      :key="state"
      class="status-bar__item flex-1 text-center mt-10 pt-12 pb-4"
      :class="{'status-bar__item--active': activeState >= index }"
    >
      {{state}}
    </div>
  </div>
</template>

<script>

export default {
  name: 'StatusBar',
  props: {
    states: Array,
    activeState: Number
  },
}
</script>


<style scoped lang="scss">
.status-bar {

  &__item {

    position: relative;

    &:after {
      content: "";
      position: absolute;
      top: 10px;
      left: 50%;
      transform: translateX(-50%);
      width: 16px;
      height: 16px;
      border-radius: 50%;
      border: 1px solid #cbd5e0;
      background-color: #FFF;
      transition: 1s background-color ease;
      z-index: 1;
    }


    &:before {
      content: "";
      width: 100%;
      height: 3px;
      position: absolute;
      top: 16px;
      right: 50%;
      background-color: #cbd5e0;
      transition: 1s background-color ease;
    }

    &:first-child:before {
      content: none;
    }

    &--active {
      &:after {
        background-color: #48bb78;
        border: none;
      }
      &:before {
        background-color: #48bb78;
      }
    }
  }

}


</style>
