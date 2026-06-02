<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-header">
        <el-icon :size="40" color="#818cf8"><Calendar /></el-icon>
        <h1>创建账户</h1>
        <p>注册一个新的账户</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleRegister" size="large">
        <el-form-item prop="username">
          <el-input v-model="form.username" placeholder="用户名" :prefix-icon="User" />
        </el-form-item>
        <el-form-item prop="email">
          <el-input v-model="form.email" placeholder="邮箱" :prefix-icon="Message" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input v-model="form.password" type="password" placeholder="密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="确认密码" :prefix-icon="Lock" show-password />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" native-type="submit" :loading="auth.loading" class="submit-btn">
            {{ auth.loading ? '注册中...' : '注 册' }}
          </el-button>
        </el-form-item>
      </el-form>

      <p class="switch-link">
        已有账户？<router-link to="/login">立即登录</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useAuthStore } from '../stores/auth.js'
import { User, Lock, Calendar, Message } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const auth = useAuthStore()
const form = reactive({ username: '', email: '', password: '', confirmPassword: '' })

const validateConfirm = (_rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请确认密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

async function handleRegister() {
  try {
    await auth.register(form.username, form.email, form.password)
  } catch (e) {
    ElMessage.error(e.message || '注册失败')
  }
}
</script>

<style scoped>
.auth-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background: radial-gradient(ellipse at 50% -20%, rgba(99,102,241,0.15), transparent 70%),
              var(--bg-base);
}
.auth-card {
  width: 420px;
  padding: 40px;
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.auth-header {
  text-align: center;
  margin-bottom: 28px;
}
.auth-header h1 {
  font-size: 24px;
  color: var(--text-primary);
  margin: 10px 0 4px;
}
.auth-header p {
  color: var(--text-muted);
  font-size: 14px;
}
.submit-btn {
  width: 100%;
}
.switch-link {
  text-align: center;
  margin-top: 16px;
  font-size: 14px;
  color: var(--text-muted);
}
</style>
