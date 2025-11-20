<script lang="ts">
  // Simple header extracted from main
  export let userName = "Ana María López";
  export let role = "Administrador";
</script>

<header class="topbar">
  <div class="controls"></div>
  <div class="top-actions">
    <div class="user">
      <div class="avatar">AM</div>
      <div class="user-info">
        <div class="name">{userName}</div>
        <div class="role">{role}</div>
      </div>
    </div>
  </div>
</header>

<style>
  .topbar {
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 28px;
    background: #f6fafc;
    border-bottom: 1px solid #eef6f9;
    position: fixed;
    top: 0;
    right: 0;
    left: 260px;
    z-index: 10;
    transition: all 0.3s ease-in-out;
  }

  .top-actions {
    display: flex;
    align-items: center;
    gap: 16px;
  }

  .user {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .avatar {
    width: 40px;
    height: 40px;
    border-radius: 999px;
    background: #9aa9ff;
    color: #fff;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
  }

  .user-info .name {
    font-weight: 600;
    color: #1e293b;
  }

  .user-info .role {
    font-size: 0.8rem;
    color: #6b7f86;
  }
</style>