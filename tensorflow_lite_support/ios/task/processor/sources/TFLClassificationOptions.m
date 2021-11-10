/* Copyright 2021 The TensorFlow Authors. All Rights Reserved.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

 http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
 ==============================================================================*/
#import "tensorflow_lite_support/ios/task/processor/sources/TFLClassificationOptions.h"

@implementation TFLClassificationOptions
@synthesize scoreThreshold;
@synthesize maxResults;
@synthesize labelAllowList;
@synthesize labelDenyList;
@synthesize displayNamesLocal;

- (id)copyWithZone:(NSZone *)zone {
  TFLClassificationOptions *classificationOptions = [[TFLClassificationOptions alloc] init];

  [classificationOptions setScoreThreshold:self.scoreThreshold];
  [classificationOptions setMaxResults:self.maxResults];
  [classificationOptions setLabelDenyList:self.labelDenyList];
  [classificationOptions setLabelAllowList:self.labelAllowList];
  [classificationOptions setDisplayNamesLocal:self.displayNamesLocal];

  return classificationOptions;
}

@end
