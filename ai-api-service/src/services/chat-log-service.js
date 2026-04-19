import { detectFraud } from './fraud-detect-service.js';

export async function analyzeChatLog({ messages, source = 'unknown' }) {
  const items = [];

  for (let index = 0; index < messages.length; index += 1) {
    const message = messages[index];
    const result = await detectFraud({
      scene: `chat-log:${message.role}`,
      source,
      text: message.text
    });

    items.push({
      index,
      role: message.role,
      text: message.text,
      ...result
    });
  }

  const flaggedItems = items.filter((item) => item.isFraud);
  const highestRiskItem =
    flaggedItems.find((item) => item.riskLevel === 'high') ||
    flaggedItems.find((item) => item.riskLevel === 'medium') ||
    items[0];

  return {
    itemCount: items.length,
    items,
    reason:
      highestRiskItem?.reason || '未发现明显诈骗特征，但仍建议结合上下文进行人工复核。',
    riskLevel: highestRiskItem?.riskLevel || 'low',
    summary:
      flaggedItems.length > 0
        ? `共发现 ${flaggedItems.length} 条可疑消息，请重点关注高风险内容。`
        : '聊天记录中未发现明显高风险消息。',
    suspiciousCount: flaggedItems.length
  };
}
