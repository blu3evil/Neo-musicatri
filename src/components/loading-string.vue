<script>
import EllipsisString from '@/components/ellipsis-string.vue'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
export default {
  components: {
    EllipsisString,
  },
  props: {
    message: {
      type: String,
      required: false,
      default: ''
    },
    placeholder: {
      type: String,
      required: false,
      default: '',
    }
  },
  setup(props) {
    const { t } = useI18n()
    const isEmptyMessage = computed(() => {
      return props.message === '' || props.message === null
    })
    const placeHolderMessage = computed(() => {
      return props.placeholder === '' || props.placeholder === null ?
        t('component.loading-string.on-loading') :
        props.placeholder
    })
    const displayMessage = computed(() => {
      return isEmptyMessage.value ? placeHolderMessage.value : props.message
    })
    return {
      isEmptyMessage,
      displayMessage
    }
  }
}
</script>
<template>
  <EllipsisString :message="displayMessage" :ellipsis="isEmptyMessage" />
</template>
<style scoped></style>
