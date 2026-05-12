<template>
  <main class="shell">
    <header class="header">
      <div>
        <h1>Internship Agent Lab</h1>
        <p>RAG-enhanced task planning agent</p>
      </div>
      <button @click="refresh">刷新</button>
    </header>

    <section class="grid">
      <article class="panel">
        <h2>系统状态</h2>
        <pre>{{ status }}</pre>
      </article>

      <article class="panel">
        <h2>知识检索</h2>
        <textarea v-model="query" rows="4" />
        <button @click="search">检索</button>
        <pre>{{ searchResult }}</pre>
      </article>

      <article class="panel">
        <h2>Agent 工具</h2>
        <pre>{{ tools }}</pre>
      </article>
    </section>
  </main>
</template>

<script setup>
import { onMounted, ref } from "vue";

const status = ref("");
const tools = ref("");
const query = ref("中冶赛迪、非科智地、未来智选共同需要哪些技术？");
const searchResult = ref("");

async function refresh() {
  const [statusResponse, toolsResponse] = await Promise.all([
    fetch("/api/system/status"),
    fetch("/api/agent/tools")
  ]);
  status.value = JSON.stringify(await statusResponse.json(), null, 2);
  tools.value = JSON.stringify(await toolsResponse.json(), null, 2);
}

async function search() {
  const response = await fetch("/api/knowledge/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: query.value, limit: 5 })
  });
  searchResult.value = JSON.stringify(await response.json(), null, 2);
}

onMounted(refresh);
</script>
