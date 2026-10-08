/** 平台适配器接口 + 任务模型。「一次任务 = 一个会话」由 CLI 层保证。 */

export interface GenJob {
  /** 提示词文件（baoyu 风格 md，含 YAML frontmatter 亦可，发送前自动剥离） */
  promptFile: string;
  /** 输出图片路径（扩展名按实际 content-type 修正） */
  outFile: string;
  /** 比例，如 16:9 / 1:1；不传则沿用会话当前值 */
  ratio?: string;
}

export interface GenResult {
  outFile: string;
  width: number;
  height: number;
  bytes: number;
}

export interface Platform {
  id: string;
  /** 打开平台并确保已登录（必要时等待用户扫码）。 */
  ensureLogin: (timeoutMs: number) => Promise<void>;
  /** 确保进入图像生成会话（一次任务只建/复用一个会话）。 */
  ensureImageSession: () => Promise<void>;
  /** 设置出图比例（如 16:9）。 */
  setRatio: (ratio: string) => Promise<void>;
  /** 校验/选择模型，返回实际生效的模型名。 */
  ensureModel: (model?: string) => Promise<string>;
  /** 在当前会话发送提示词并等待出图，全部新图并发下载落盘（[0] 占用 job.outFile，其余加 -N 序号）。 */
  generate: (job: GenJob, seen: Set<string>, timeoutMs: number) => Promise<GenResult[]>;
}
