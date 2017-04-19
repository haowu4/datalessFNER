echo "" > eval.bg_only.log
python dfiner/eval/eval_subset.py /tmp/bg_only eval_output/organized/figer/figer.out.fine_only >> eval.bg_only.log
echo "" >> eval.bg_only.log
echo "" >> eval.bg_only.log
python dfiner/eval/eval_subset.py /tmp/bg_only eval_output/organized/ucl/ucl.out.fine_only >> eval.bg_only.log
echo "" >> eval.bg_only.log
echo "" >> eval.bg_only.log
python dfiner/eval/eval_subset.py /tmp/bg_only eval_output/organized/outs/figer.out.fine_only >> eval.bg_only.log
echo "" >> eval.bg_only.log
echo "" >> eval.bg_only.log


echo "" > eval.context_only.log
python dfiner/eval/eval_subset.py /tmp/context_only eval_output/organized/figer/figer.out.fine_only >> eval.context_only.log
echo "" >> eval.context_only.log
echo "" >> eval.context_only.log
python dfiner/eval/eval_subset.py /tmp/context_only eval_output/organized/ucl/ucl.out.fine_only >> eval.context_only.log
echo "" >> eval.context_only.log
echo "" >> eval.context_only.log
python dfiner/eval/eval_subset.py /tmp/context_only eval_output/organized/outs/figer.out.fine_only >> eval.context_only.log
echo "" >> eval.context_only.log
echo "" >> eval.context_only.log