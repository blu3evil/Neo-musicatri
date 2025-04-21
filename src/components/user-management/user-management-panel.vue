<script>
import UserAvatarV2 from '@/components/user-avatar-v2.vue'
import { useStore } from 'vuex'
import { computed } from 'vue'

export default {
  components: { UserAvatarV2 },
  props: {
    id: {
      type: String,
      required: true
    },
    avatar: {
      type: String,
      required: true
    }
  },
  setup() {
    const store = useStore()
    return {

    }
  },
}
</script>
<template>
<!--  <el-row>-->
<!--    &lt;!&ndash; 用户头像 &ndash;&gt;-->
<!--    <el-col :span="6">-->
<!--      <UserAvatarV2-->
<!--        :user-avatar-context="currentUserAvatarContext"-->
<!--        class="user-avatar"-->
<!--        :click-to-refresh="true"-->
<!--      />-->
<!--    </el-col>-->
<!--    <el-col :span="18">-->
<!--      <div class="text-small" style="margin-top: 2px">-->
<!--        <el-row>{{ currentUser.username }}</el-row>-->
<!--        <el-row>id:{{ currentUser.id }}</el-row>-->
<!--      </div>-->
<!--    </el-col>-->
<!--  </el-row>-->
</template>
<style></style>
