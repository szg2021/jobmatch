<template>
  <PageContentWrapper className="candidate-recommendations-container">
    <page-header
      title="人才推荐"
      subtitle="为您的职位寻找最匹配的候选人"
    />
    
    <el-card shadow="hover">
      <el-result
        icon="info"
        title="功能开发中"
        sub-title="人才推荐功能即将上线，敬请期待"
      >
        <template #extra>
          <el-button type="primary">返回首页</el-button>
        </template>
      </el-result>
    </el-card>
  </PageContentWrapper>
</template>

<script lang="ts" setup>
import PageHeader from '@/components/common/PageHeader.vue';
import PageContentWrapper from '@/components/layout/PageContentWrapper.vue';
</script>

<style scoped>
.candidate-recommendations-container {
  max-width: 1200px;
  margin: 0 auto;
}
</style> 