declare module 'react-katex' {
  import { ComponentType } from 'react';

  export interface KatexOptions {
    displayMode?: boolean;
    throwOnError?: boolean;
    errorColor?: string;
    macros?: Record<string, string>;
    colorIsTextColor?: boolean;
    maxSize?: number;
    maxExpand?: number;
    allowedProtocols?: string[];
    strict?: boolean | string | ((errorCode: string, errorMsg: string, token: any) => boolean);
    trust?: boolean | ((context: any) => boolean);
    fleqn?: boolean;
    leqno?: boolean;
    output?: 'html' | 'mathml' | 'htmlAndMathml';
  }

  export interface MathComponentProps {
    math: string;
    errorColor?: string;
    renderError?: (error: Error) => React.ReactNode;
    settings?: KatexOptions;
  }

  export const InlineMath: ComponentType<MathComponentProps>;
  export const BlockMath: ComponentType<MathComponentProps>;
}
