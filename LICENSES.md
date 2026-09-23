# GestureForge Licences and Source Attribution

Status: draft. Verify exact installed package licences before submission. Pinned versions are recorded in `requirements.lock`.

## Runtime Dependencies

| Dependency | Planned use | Licence check status |
| --- | --- | --- |
| Python 3.11.16 | Runtime | Version reported by implementation lane; licence check pending |
| PySide6 6.11.2 | Desktop widgets | Pending installed-package licence check |
| opencv-contrib-python 5.0.0.93 | Camera capture and image conversion | Pending installed-package licence check |
| MediaPipe 1.0.1 | Hand landmarks | Pending installed-package licence check |
| NumPy 2.4.6 | Numeric arrays | Pending installed-package licence check |
| scikit-learn 1.9.1 | kNN, SVM, scaling, metrics | Pending installed-package licence check |
| pytest 9.1.1 | Automated tests | Pending installed-package licence check |

See `requirements.lock` for the full pinned package set. Confirm licences from installed package metadata before submission.

## Research and Technical References

- Zhang, F. et al. (2020). MediaPipe Hands: On-device Real-time Hand Tracking. https://arxiv.org/abs/2006.10214
- Wobbrock, J. O., Wilson, A. D., and Li, Y. (2007). Gestures without libraries, toolkits or training: a $1 recognizer for user interface prototypes. https://depts.washington.edu/acelab/proj/dollar/index.html
- Cover, T. and Hart, P. (1967). Nearest Neighbor Pattern Classification. https://isl.stanford.edu/~cover/papers/transIT/0021cove.pdf
- Cortes, C. and Vapnik, V. (1995). Support-vector networks. https://doi.org/10.1007/BF00994018
- NASA. 3.0 NASA Program/Project Life Cycle. https://www.nasa.gov/reference/3-0-nasa-program-project-life-cycle/

## Attribution Notes

MediaPipe provides pretrained hand landmarks. GestureForge must credit MediaPipe and must not imply that the project team trained the landmark detector.

scikit-learn provides the classifier implementations. GestureForge's contribution is dataset design, feature extraction, classifier comparison, rejection policy, controller integration, and evaluation.

## Before Submission

- Run `python -m pip freeze` in the final virtual environment and save the output in the release evidence.
- Check installed package metadata with `python -m pip show <package>`.
- Record model asset sources and checksums if MediaPipe model files are bundled.
- Include only data and assets that the team is permitted to submit.
