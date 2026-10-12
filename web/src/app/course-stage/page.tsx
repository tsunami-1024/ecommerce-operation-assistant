import Link from 'next/link';

export default function CourseStagePage() {
  return <main className="mx-auto max-w-3xl p-10">
    <h1 className="text-2xl font-semibold">当前学习阶段：基础业务系统</h1>
    <p className="my-5">模型配置、自动诊断、创意生成、图片视频生成及 Agent 能力将在 04、05 篇接入。当前可使用商品、库存、竞品、导入、经营数据和人工方案管理。</p>
    <p className="mb-5">用户管理通过后端 Swagger 的 users 接口完成。示范资料请按笔记手工创建，本阶段不导入带有模拟生成结果的演示数据。</p>
    <Link href="/" className="text-blue-700 underline">返回工作台</Link>
  </main>;
}
