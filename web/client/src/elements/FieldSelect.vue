<template>
<div class="flex flex-row w-full justify-center items-center">
    <div 
        v-for="(val, i) in values"
        :key="val"
        @click="$emit('changeLang', i)"
        :class="{'text-white bg-gray-700': i === activeValue, 'rounded-r-none': i === 0, 'rounded-l-none border-r': i === values.length - 1}"
        class="cursor-pointer px-3 py-2 text-sm border border-gray-700 rounded rounded-xl border-r-0 h-full flex items-center  justify-center">
        {{val}}
    </div>
</div>
</template>

<script>

export default {
  name: 'FieldSelect',
  props: {
    values: Array,
    activeValue: Number
  },
}
</script>
